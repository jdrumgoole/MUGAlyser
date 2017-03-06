
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
    from_date = getDate( from_date_string )
    to_date = getDate( to_date_string )
    
    return ( from_date, to_date )

    
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
            
    def __init__(self, mdb, ext, start_date, end_date, root ):
        self._mdb = mdb
        audit = Audit( mdb )
    
        self._batchID = audit.getCurrentValidBatchID()
        self._start_date = start_date
        self._end_date = end_date
        self._ext = ext
        self._root = root
        self._files = []
       
    def _membersAggregate(self, batchIDs, urls ):
        agg = Agg( self._mdb.groupsCollection())
        
        agg.addMatch({ "batchID"       : { "$in" : batchIDs},
                       "group.urlname" : { "$in" : urls }} )
         
        agg.addProject(  { "_id" : 0, 
                           "urlname" : "$group.urlname", 
                           "country" : "$group.country",
                           "batchID" : 1, 
                           "member_count" : "$group.member_count" })
        agg.addSort( Sorter("member_count", pymongo.DESCENDING ))
        
        return agg
    
    def getMembers( self, urls, filename=None ):
        
        agg = self._membersAggregate( [self._batchID], urls)

        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "urlname", "country", "batchID", "member_count"] )
        
        
    def getRSVPHistory(self, urls, filename=None ):
                
        agg = Agg( self._mdb.pastEventsCollection())  
        
        agg.addMatch({ "event.group.urlname" : { "$in" : urls }} )
        
        agg.addProject( { "timestamp" : Agg.cond( { "$eq": [ { "$type" : "$event.time" }, "date" ]},
                                                  { "$dateToString" : { "format" : "%Y", #-%m-%d",
                                                    "date"          :"$event.time"}},
                                                    None  ),
                          "event"     : "$event.name",
                          "country"    : "$event.venue.country",
                          "rsvp_count" : "$event.yes_rsvp_count" } )
        
        agg.addMatch( { "timestamp" : { "$ne" : None }} )
        agg.addGroup( { "_id" :"$timestamp",
                        #"event" : { "$addToSet" : { "event" : "$event", "country" : "$country" }},
                        "rsvp_count" : { "$sum" : "$rsvp_count"}})
        sorter = Sorter()
        sorter.add( "_id" )
        agg.addSort( sorter )
        
            
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "_id", "rsvp_count" ] )


    def getMemberHistory(self, urls, filename=None ):
        
        audit = Audit( self._mdb )
        
        validBatches = list( audit.getCurrentValidBatchIDs())
                
        agg = Agg( self._mdb.groupsCollection())
        
        agg.addMatch({ "batchID"       : { "$in" : validBatches },
                       "group.urlname" : { "$in" : urls }} )

        agg.addProject({ "timestamp" : { "$dateToString" : { "format" : "%Y-%m-%d",
                                                             "date"    :"$timestamp"}},
                         "batchID" : 1,
                         "urlname" : "$group.urlname",
                         "count" : "$group.member_count" } )
        
        agg.addGroup( { "_id" : { "ts": "$timestamp", "batchID" : "$batchID" },
                        "groups" : { "$addToSet" : "$urlname" },
                        "count" : { "$sum" : "$count"}})

        sorter = Sorter()
        sorter.add( "_id.batchID" )
        agg.addSort( sorter )
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "_id", "groups", "count" ] )
        
    def getGroupInsight( self, urlname ):
        
        groups = self._mdb.groupsCollection()
        agg = Agg( groups )
        agg.addMatch( { "batchID" : self._batchID, "group.urlname" : urlname })
        agg.addProject(  { "_id" : 0, "urlname" : "$group.urlname", "member_count" : "$group.member_count" })
    
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
        
        agg.addSort( Sorter( "year" ))

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
        
        agg = Agg( self._mdb.groupsCollection())
        agg.addMatch( { "batchID" : self._batchID,
                        "group.urlname" : { "$in" : urls }} )
        
        agg.addRangeSearch( "group.founded_date", self._start_date, self._end_date )
        agg.addProject( { "_id" : 0,
                          "urlname" : "$group.urlname",
                          "founded" :  { "$dateToString" : { "format" : "%Y-%m-%d",
                                                            "date"    :"$group.founded_date"}}} )
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "urlname", "founded" ] )
        
    def groupTotals( self, urls, filename=None ):
    
        agg = Agg( self._mdb.pastEventsCollection())
    
        agg.addMatch({ "batchID"             : self._batchID,
                       "event.status"        : "past",
                       "event.group.urlname" : { "$in" : urls }} )
        
        agg.addGroup( { "_id" : { "urlname" : "$event.group.urlname", 
                                  "year"    : { "$year" : "$event.time"}},
                        "event_count" : { "$sum" : 1 },
                        "rsvp_count"  : { "$sum" : "$event.yes_rsvp_count" }})
        agg.addProject( { "_id" : 0,
                          "group"   : "$_id.urlname",
                          "year"    : "$_id.year",
                          "event_count" : 1,
                          "rsvp_count" : 1 } )
    
        sorter = Sorter()
        sorter.add( "year" )
        sorter.add( "group" )
        sorter.add( "event_count")
        sorter.add( "rsvp_count" )
        
        agg.addSort( sorter )
    
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "year", "group", "country", "event_count", "rsvp_count"] )
    
        
    def get_events(self, urls, rsvpbound=0, filename=None):
    
        agg = Agg( self._mdb.pastEventsCollection())
        
        agg.addMatch({ "batchID"      : self._batchID,
                       "event.status" : "past",
                       "event.group.urlname" : { "$in" : urls }} )
            
        agg.addRangeSearch( "event.time", self._start_date, self._end_date )
        
        agg.addProject( { "_id": 0, 
                          "group"        : u"$event.group.urlname", 
                          "name"         : u"$event.name",
                          "rsvp_count"   : "$event.yes_rsvp_count",
                          "date"         : { "$dateToString" : { "format" : "%Y-%m-%d",
                                                                 "date"   :"$event.time"}}} ) 
     
        sorter = Sorter( "group")
        sorter.add( "rsvp_count")
        sorter.add( "date")
        agg.addSort(  sorter )
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "group", "name", "rsvp_count", "date" ] )
        
    def get_newMembers( self, urls, filename=None ):
        
        agg = Agg( self._mdb.membersCollection())
        
        agg.addUnwind( "$member.chapters" )
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "member.chapters.urlname" : { "$in" : urls }} )

        agg.addRangeSearch( "member.join_time", self._start_date, self._end_date )
        
        agg.addProject( { "_id" : 0,
                          "group"     : "$member.chapters.urlname",
                          "name"      : "$member.member_name",
                          "join_date" : { "$dateToString" : { "format" : "%d-%m-%Y",
                                                              "date"   :"$member.join_time"}}} )
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "group", "name", "join_date" ] )
        
    def get_rsvps( self, urls, rsvpbound=0, filename=None):   
    
        agg = Agg( self._mdb.attendeesCollection())
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "info.event.group.urlname" : { "$in" : urls }} )
        
        agg.addRangeSearch( "info.event.time", self._start_date, self._end_date )
        
        agg.addProject( { "_id"        : 0,
                          "attendee"   : "$info.attendee.member.name", 
                          "group"      : "$info.event.group.urlname",
                          "event_name" : "$info.event.name" })
        
        agg.addGroup( { "_id" : {  "attendee": "$attendee", "group": "$group" },
                        "event_count" : { "$sum" : 1 }})
                        
        agg.addProject( { "_id" : 0,
                          "attendee" : "$_id.attendee",
                          "group" : "$_id.group",
                          "event_count" : 1 } )
        
        agg.addSort( Sorter( "event_count"))
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "attendee", "group", "event_count" ] )

    
    def get_active( self, urls, filename=None ):
        '''
        We define an active user as somebody who has rsvp'd to at least one event in the last six months.
        '''
        agg = Agg( self._mdb.attendeesCollection())
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "info.event.group.urlname" : { "$in" : urls },
                       "info.attendee.rsvp.response" : "yes" } )
        
        agg.addRangeSearch( "info.event.time", self._start_date, self._end_date )
        
    #     agg.addProject( { "_id" : 0,
    #                       "name" : "$info.attendee.member.name",
    #                       "urlname" : "$info.event.group.urlname",
    #                       "event_name" : "$info.event.name" })
    
        agg.addGroup( { "_id"    : "$info.attendee.member.name",
                        "count"  : { "$sum": 1 },
                        "groups" : { "$addToSet" : "$info.event.group.urlname" }} )
        
        agg.addSort( Sorter( "count" ))
        
        formatter = AggFormatter( agg, self._root, filename, self._ext )
        formatter.output( fieldNames= [ "_id", "count", "groups" ] )

def main( args ):
    
#if __name__ == '__main__':
    
    cmds = [ "meetuptotals", "grouptotals", "groups",  "members", "events", "rsvps", "active", "newmembers", "memberhistory", "rsvphistory" ]
    parser = ArgumentParser( args )
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--format", default="JSON", choices=[ "JSON", "json", "CSV", "csv" ], help="format for output [default: %(default)s]" )
    parser.add_argument( "--root", default="-", help="filename root for output [default: %(default)s]" )
    parser.add_argument( "--stats",  nargs="+", default=[ "groups" ], 
                         choices= cmds,
                         help="List of stats to output [default: %(default)s]" )
    parser.add_argument( "--country", nargs="+", default=[ "all"],
                         help="pick a region { all| EU | NORDICS } to report on [default: %(default)s]")
    
    parser.add_argument( "--url", nargs="+",
                         help="pick a URL for a group to report on [default: %(default)s]")

    parser.add_argument( "--start", help="Starting date range for a query" )
    
    parser.add_argument( "--end", help="Ending date range for a query" )
    
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
        ( from_date, to_date ) = getDateRange( args.start, args.end )
    except ValueError, e:
        print( "Bad date: %s" % e )
        sys.exit( 2 )

    analytics = MUG_Analytics( mdb, args.format.lower(), from_date, to_date, root )
    
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
