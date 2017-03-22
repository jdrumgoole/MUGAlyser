#!/usr/bin/env python
'''
Created on 28 Dec 2016
@author: jdrumgoole
'''

import pprint
import pymongo
import csv
import sys

from argparse import ArgumentParser

from dateutil.parser import parse
from pydrive import auth
from pydrive.drive import GoogleDrive


from mugalyser.agg import Agg, Sorter, AggFormatter
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from mugalyser.groups import EU_COUNTRIES, NORDICS_COUNTRIES, Groups
from mugalyser.members import Members

import contextlib
    
def getDate( date_string ):
    if date_string is None :
        return None
    else:
        retVal = parse( date_string )
        return retVal

def getDateRange( from_date_string, to_date_string ):
    '''
    parse a date range. Return none if ranges are none.
    '''
    
    if from_date_string:
        try :
            from_date = getDate( from_date_string )
        except ValueError :
            print( "Ignoring --from date: '%s' not a valid date")
            from_date = None
    else:
        from_date = None
        
    if to_date_string:
        try :
            to_date = getDate( to_date_string )
        except ValueError:
            print( "Ignoring --to date: '%s' not a valid date" )
            to_date = None
    else:
        to_date = None
    
    if from_date and to_date:
        if to_date >= from_date  :
            return ( from_date, to_date )
        else:
            print( "--from date ('%s') is greater than --to date ('%s') ignoring these parameters" % ( from_date, to_date ))
            return ( None, None )
    else:
        return( None, None )

    
def addJoinDate( mdb, cursor ):
    
    members = Members( mdb )
    for i in cursor :
        member = members.get_by_ID( i[ "info"]["attendee"]["member"][ "id"])
        i[ "join_date"] = member[ "join_time" ]
        yield i
        
def addCountry( mdb, cursor ):
    groups = Groups( mdb )
    for i in cursor:
        country = groups.get_country( i[ 'group'] )
        i[ "country"] = country
        yield i    
        
class MUG_Analytics( object ):
            
    def __init__(self, mdb, ext, root, sorter=None ):
        self._mdb = mdb
        audit = Audit( mdb )
    
        self._batchID = audit.getCurrentValidBatchID()
        self._sorter = sorter
        self._start_date = None
        self._end_date = None
        self._ext = ext
        self._root = root
        self._files = []
        self._sort_field = None
        self._sort_direction = None
    
    
    def setRange(self, start_date, end_date ):
        self._start_date = start_date
        self._end_date = end_date

        
    def setSort(self, sort_field, sort_direction ):
        self._sort_field = sort_field
        self._sort_direction = sort_direction
        
    def getMembers( self, urls, filename=None ):
        '''
        Get a count of the members for each group in "urls"
        Range doens't make sense here so its not used. If supplied it is ignored.
        '''
        
        agg = Agg( self._mdb.groupsCollection())
        
        agg.addMatch({ "batchID"       : { "$in" : [ self._batchID ]},
                       "group.urlname" : { "$in" : urls }} )
         
        agg.addProject(  { "_id" : 0, 
                           "urlname" : "$group.urlname", 
                           "country" : "$group.country",
                           "batchID" : 1, 
                           "member_count" : "$group.member_count" })
        
        if self._sorter:
            agg.addSort( self._sorter)
            
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "urlname", "country", "batchID", "member_count"] )
        
    def getRSVPHistory(self, urls, filename=None ):
        '''
        Get the list of past events for groups (urls) and report on the date of the event
        and the number of RSVPs.
        '''
                
        agg = Agg( self._mdb.pastEventsCollection())  
        
        agg.addMatch({ "event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "event.time", self._start_date, self._end_date )
            
        agg.addProject( { "timestamp" : "$event.time", 
                          "event"     : "$event.name",
                          "country"    : "$event.venue.country",
                          "rsvp_count" : "$event.yes_rsvp_count" } )
        
        agg.addMatch( { "timestamp" : { "$type" : "date" }} )
        agg.addGroup( { "_id" :"$timestamp",
                        #"event" : { "$addToSet" : { "event" : "$event", "country" : "$country" }},
                        "rsvp_count" : { "$sum" : "$rsvp_count"}})
        
        if self._sorter :
            agg.addSort( self._sorter)
            
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "_id", "rsvp_count" ], datemap=[ "_id"] )

    def getMemberHistory(self, urls, filename=None ):
        '''
        Got into every batch and see what the member count was for each group (URL) this uses all 
        the batches to get a history of a group.
        Range is used to select batches in this case via the "timestamp" field.
        '''
        audit = Audit( self._mdb )
        
        validBatches = list( audit.getCurrentValidBatchIDs())
                
        agg = Agg( self._mdb.groupsCollection())
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "timestamp", self._start_date, self._end_date )
        
        agg.addMatch({ "batchID"       : { "$in" : validBatches },
                       "group.urlname" : { "$in" : urls }} )
            
        agg.addProject({ "timestamp" : 1,
                         "batchID" : 1,
                         "urlname" : "$group.urlname",
                         "count" : "$group.member_count" } )
        
        agg.addGroup( { "_id" : { "ts": "$timestamp", "batchID" : "$batchID" },
                        "groups" : { "$addToSet" : "$urlname" },
                        "count" : { "$sum" : "$count"}})

        if self._sorter :
            agg.addSort( self._sorter)

        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "_id", "groups", "count" ], datemap=[ "_id.ts" ])
    
    def get_group_names( self, region_arg ):
        
        groups = Groups( self._mdb )
        if region_arg == "EU" :
            urls = groups.get_region_group_urlnames( EU_COUNTRIES )
        elif region_arg == "US" :
            urls = groups.get_region_group_urlnames( [ "USA" ] )
        else:
            urls = groups.get_region_group_urlnames()
            
        return urls
        
    def meetupTotals( self, urls, filename=None ):
            
        agg = Agg( self._mdb.pastEventsCollection())                                       
        
        agg.addMatch({ "batchID"      : self._batchID,
                       "event.status" : "past",
                       "event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "event.time", self._start_date, self._end_date )
            
        agg.addProject( { "_id"   : 0, 
                          "name"  : "$event.name", 
                          "time"  : "$event.time",  
                          "rsvp"  : "$event.yes_rsvp_count" } )
        
        agg.addGroup( { "_id"          : { "$year" : "$time"}, 
                        "total_rsvp"   : { "$sum" : "$rsvp"},
                        "total_events" : { "$sum" : 1 }})
        
        agg.addProject( { "_id" : 0,
                          "year"         : "$_id",
                          "total_rsvp"   : 1,
                          "total_events" : 1 } )
        
        if self._sorter:
            agg.addSort( self._sorter)

        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "year", "total_rsvp", "total_events" ] )
    
    def batchMatch( self, collection ):
        agg = Agg( collection )
        agg.addMatch({ "batchID" : self._batchID } )
        return agg
    
    def matchGroup( self, urlname ):
        agg = Agg( self._mdb.pastEventsCollection())
        agg.addMatch({ "batchID"      : self._batchID, 
                       "event.status" : "past", 
                       "event.group.urlname" : urlname } )
        return agg
    
    def get_groups( self, urls, filename=None  ):
        '''
        Get all the groups listed by urls and their start dates
        '''
        
        agg = Agg( self._mdb.groupsCollection())
        agg.addMatch( { "batchID" : self._batchID,
                        "group.urlname" : { "$in" : urls }} )
        
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "group.founded_date", self._start_date, self._end_date )
            
        agg.addProject( { "_id" : 0,
                          "urlname" : "$group.urlname",
                          "members" : "$group.member_count",
                          "founded" : "$group.founded_date" } )

        if self._sorter:
            agg.addSort( self._sorter)        
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "urlname", "members", "founded" ], datemap=[ "founded" ] )
        
    def groupTotals( self, urls, filename=None ):
        '''
        get the total number of RSVPs by group.
        '''
    
        agg = Agg( self._mdb.pastEventsCollection())
    
        agg.addMatch({ "batchID"             : self._batchID,
                       "event.status"        : "past",
                       "event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "groups.founded_date", self._start_date, self._end_date )
            
        agg.addGroup( { "_id" : { "urlname" : "$event.group.urlname", 
                                  "year"    : { "$year" : "$event.time"}},
                        "event_count" : { "$sum" : 1 },
                        "rsvp_count"  : { "$sum" : "$event.yes_rsvp_count" }})
        
        agg.addProject( { "_id" : 0,
                          "group"   : "$_id.urlname",
                          "year"    : "$_id.year",
                          "event_count" : 1,
                          "rsvp_count" : 1 } )
        
        if self._sorter:
            agg.addSort( self._sorter )
    
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "year", "group", "event_count", "rsvp_count"] )
    
        
    def get_events(self, urls, rsvpbound=0, filename=None):
    
        agg = Agg( self._mdb.pastEventsCollection())
        
        agg.addMatch({ "batchID"      : self._batchID,
                       "event.status" : "past",
                       "event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "event.time", self._start_date, self._end_date )
            
        agg.addProject( { "_id": 0, 
                          "group"        : u"$event.group.urlname", 
                          "name"         : u"$event.name",
                          "rsvp_count"   : "$event.yes_rsvp_count",
                          "date"         :"$event.time" }) 
     
        if self._sorter:
            agg.addSort( self._sorter)
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "group", "name", "rsvp_count", "date" ], datemap=[ "date"])
        
    def get_newMembers( self, urls, filename=None ):
        '''
        Get all the members of all the groups (urls). Range is join_time.
        '''
        
        agg = Agg( self._mdb.membersCollection())
        
        agg.addUnwind( "$member.chapters" )
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "member.chapters.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "member.join_time", self._start_date, self._end_date )
            
        agg.addProject( { "_id" : 0,
                          "group"     : "$member.chapters.urlname",
                          "name"      : "$member.member_name",
                          "join_date" : "$member.join_time" } )
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "group", "name", "join_date" ], datemap=[ 'join_date'])
        
    def get_rsvps( self, urls, rsvpbound=0, filename=None):   
    
        agg = Agg( self._mdb.attendeesCollection())
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "info.event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "info.event_time", self._start_date, self._end_date )
        
        agg.addProject( { "_id"        : 0,
                          "attendee"   : "$info.attendee.member.name", 
                          "group"      : "$info.event.group.urlname",
                          "event_time" : "$info.event_time",
                          "event_name" : "$info.event.name" })
        
        agg.addGroup( { "_id" : {  "attendee": "$attendee", "group": "$group" },
                        "event_count" : { "$sum" : 1 }})
                        
        agg.addProject( { "_id" : 0,
                          "attendee" : "$_id.attendee",
                          "group" : "$_id.group",
                          "event_time" : 1,
                          "event_count" : 1 } )
        
        if self._sorter :
            agg.addSort( self._sorter)
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "attendee", "group", "event_time", "event_count" ] )

    
    def get_active( self, urls, filename=None ):
        '''
        We define an active user as somebody who has rsvp'd to at least one event in the last six months.
        '''
        agg = Agg( self._mdb.attendeesCollection())
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "info.event.group.urlname" : { "$in" : urls },
                       "info.attendee.rsvp.response" : "yes" } )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "info.event_time", self._start_date, self._end_date )
        
    #     agg.addProject( { "_id" : 0,
    #                       "name" : "$info.attendee.member.name",
    #                       "urlname" : "$info.event.group.urlname",
    #                       "event_name" : "$info.event.name" })
    
        agg.addGroup( { "_id"    : "$info.attendee.member.name",
                        "count"  : { "$sum": 1 },
                        "groups" : { "$addToSet" : "$info.event.group.urlname" }} )
        
        if self._sorter :
            agg.addSort( self._sorter)
            
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "_id", "count", "groups" ] )

def convert_direction( arg ):
    
    if arg == "ascending" :
        return pymongo.ASCENDING
    elif arg == "descending" :
        return pymongo.DESCENDING
    else:
        return pymongo.ASCENDING
    
def main( args ):
    
#if __name__ == '__main__':
    
    cmds = [ "meetuptotals", "grouptotals", "groups",  "members", "events", "rsvps", "active", "newmembers", "memberhistory", "rsvphistory" ]
    parser = ArgumentParser( args )
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--format", default="JSON", choices=[ "JSON", "json", "CSV", "csv" ], help="format for output [default: %(default)s]" )
    parser.add_argument( "--root", default="-", help="filename root for output [default: %(default)s for stdout]" )
    parser.add_argument( "--stats",  nargs="+", default=[ "groups" ], 
                         choices= cmds,
                         help="List of stats to output [default: %(default)s]" )
    parser.add_argument( "--country", nargs="+", default=[ "all"],
                         help="pick a region { all| EU | NORDICS } to report on [default: %(default)s]")
    
    parser.add_argument( "--url", nargs="+",
                         help="pick a URL for a group to report on [default: %(default)s]")

    parser.add_argument( "--start", help="Starting date range for a query" )
    
    parser.add_argument( "--end", help="Ending date range for a query" )
    
    parser.add_argument( "--sort", action="append", help="Sort the output using this field")
    
    parser.add_argument( "--direction", action="append", choices=[ "ascending", "descending" ], 
                         default=[], help="Sort direction [default: %(default)s] ")
    
    parser.add_argument( "--upload", default=False, action="store_true",  help="upload to gdrive" )
    
    parser.add_argument( "--gdrive_config", default="pydrive_auth.json", help="use this gdrive config [default: %(default)s]" )
    
    args = parser.parse_args()
    
    upload_List = []
    
    root = args.root
    
    if root is None:
        root = "-"
    
    mdb = MUGAlyserMongoDB( uri=args.host )
        
    groups = Groups( mdb )
    
    if args.url :
        urls = args.url
    else:
        if "all" in args.country :
            urls = groups.get_region_group_urlnames()
        elif "EU" in args.country :
            urls = groups.get_region_group_urlnames( EU_COUNTRIES )
        elif "NORDICS" in args.country :
            urls = groups.get_region_group_urlnames( NORDICS_COUNTRIES )
        else:
            urls = groups.get_region_group_urlnames( args.country )

    try :
        ( start_date, end_date ) = getDateRange( args.start, args.end )
    except ValueError, e:
        print( "Bad date: %s" % e )
        sys.exit( 2 )

    sort_direction = None
    
    sorter=None
    if args.sort :
        sorter = Sorter()
        for i in range( len( args.sort )) :
            if i < len( args.direction )  :
                sorter.add_sort( args.sort[ i ], convert_direction( args.direction[ i ]))
            else:
                sorter.add_sort( args.sort[ i ], pymongo.ASCENDING )
                
    
    analytics = MUG_Analytics( mdb, args.format.lower(), root, sorter )
    analytics.setRange(start_date, end_date)
    
    if args.sort :
        analytics.setSort( args.sort, sort_direction )
    
    if "meetuptotals" in args.stats :
        analytics.meetupTotals( urls, filename="meetuptotals" )
        
    if "grouptotals" in args.stats :
        analytics.groupTotals( urls, filename="grouptotals" )
        
    if "groups" in args.stats :
        analytics.get_groups( urls, filename="groups" )
    
    if "members" in args.stats :
        analytics.getMembers( urls, filename="members" )

    if "events" in args.stats:
        analytics.get_events( urls, filename="events" )
        
    if "rsvps" in args.stats:
        analytics.get_rsvps( urls, filename="rsvps" )
        
    if "active" in args.stats:
        analytics.get_active(  urls, filename="active" )

    if "newmembers" in args.stats :
        analytics.get_newMembers( urls, filename="newmembers" )
        
    if "memberhistory" in args.stats :
        analytics.getMemberHistory(urls,  filename="memberhistory")
        
    if "rsvphistory" in args.stats :
        analytics.getRSVPHistory(urls, filename="rsvphistory")
        
    if args.upload :
        gauth = auth.GoogleAuth()
        gauth.LoadClientConfigFile( args.gdrive_config )
        
        drive = GoogleDrive(gauth)
        
        for i in analytics.files() :
            file1 = drive.CreateFile({'title': i})  # Create GoogleDriveFile instance with title 'Hello.txt'.
            file1.SetContentFile( i ) # Set content of the file from given string.
            file1.Upload()

if __name__ == '__main__':
    main( sys.argv )
