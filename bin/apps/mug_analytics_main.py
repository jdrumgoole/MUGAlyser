#!/usr/bin/env python
'''
Created on 28 Dec 2016
@author: jdrumgoole
'''

import pprint
import pymongo
import sys
import datetime

from argparse import ArgumentParser, ArgumentTypeError

from dateutil.parser import parse
from mugalyser.gdrive import GDrive


from mongodb_utils.agg import Agg, Sorter, CursorFormatter
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from mugalyser.groups import EU_COUNTRIES, NORDICS_COUNTRIES, Groups
from mugalyser.members import Members
from mugalyser.events import PastEvents

import contextlib
    
def get_date( date_string ):
    if date_string is None :
        return None
    else:
        retVal = parse( date_string )
        return retVal

def valid_date( date_string ):
    try :
        return get_date( date_string )
    except ValueError :
        raise ArgumentTypeError( "'%s' cannot be parsed as a date" % date_string )
    
def getDateRange( start_date, end_date ):
    '''
    parse a date range. Return none if ranges are none.
    '''
    
    if start_date and end_date:
        if end_date >= start_date  :
            return ( start_date, end_date )
        else:
            print( "--start date ('%s') is greater than --end date ('%s') ignoring these parameters" % ( start_date, end_date ))
            return ( None, None )
    else:
        return( start_date, end_date )

    
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
        
class Filename( object ):
    '''
    Make a filename but accept an "-" as the name parameter. If the name
    is "-" then ignore all other parameters and write to stdout. So return
    just "-" as the filename.
    '''
    def __init__(self, prefix="", name="-", suffix="", ext=""):
        self._prefix = prefix
        self._name = name
        self._suffix = suffix
        self._ext = ext
        
        self._filename = self.make( self._name )
        
    def __call__(self, suffix=""):
        return self.make( suffix = suffix )
    
    def __str__(self):
        return self._filename
    
    def __repr__(self):
        return self._filename
    
    def make( self, suffix ):
        '''
        If root is '-" then we just return that. Otherwise
        we construct a filename of the form:
        <root><suffix>.<ext>
        '''
        
        if self._name == "-"  or self._name is None:
            return "-"
        else: 
            return self._prefix + self._name + self._suffix + "." + self._ext

        
class MUG_Analytics( object ):
            
    def __init__(self, mdb, output_filename="-", formatter="json", batchID=None, limit=None ):
        self._mdb = mdb
        audit = Audit( mdb )
    

        self._sorter = None
        self._start_date = None
        self._end_date = None
        self._filename = output_filename
        self._format = formatter
        self._files = []
        self._limit = limit

        if batchID is None:
            self._batchID = audit.getCurrentValidBatchID()
        else:
            self._batchID = batchID
            
        self._pro_account = audit.isProBatch( self._batchID )
    
    def files(self):
        return self._files
    
    def setRange(self, start_date, end_date ):
        self._start_date = start_date
        self._end_date = end_date      
        
    def setSort(self, sorter ):
        self._sorter = sorter
        
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
            
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg.aggregate(), self._filename, self._format )
        formatter.output( fieldNames= [ "urlname", "country", "batchID", "member_count"] )
        
    def get_RSVP_history(self, urls, filename=None ):
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
            
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg.aggregate(), self._filename, self._format )
        filename = formatter.output( fieldNames= [ "_id", "rsvp_count" ], datemap=[ "_id"], limit=self._limit )
        
        if filename != "-":
            self._files.append( filename )

    def get_member_history(self, urls, filename=None ):
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
        
        agg.addProject({ "_id": 0,
                        "timestamp" : 1,
                         "batchID" : 1,
                         "urlname" : "$group.urlname",
                         #"count" : "$group.members" } )
                         "count" : Agg.ifNull( "$group.member_count", "$group.members")})


        

        agg.addGroup( { "_id" : { "ts": "$timestamp", "batchID" : "$batchID" },
                        "groups" : { "$addToSet" : "$urlname" },
                        "count" : { "$sum" : "$count"}})
        
        #CursorFormatter( agg.aggregate()).output()
        
        if self._sorter :
            agg.addSort( self._sorter)
            
        #CursorFormatter( agg.aggregate()).output()
        if filename :
            self._filename = filename

        print( agg )
        formatter = CursorFormatter( agg.aggregate(), self._filename, self._format )
        formatter.output( fieldNames= [ "_id", "groups", "count" ], datemap=[ "_id.ts" ], limit=self._limit)
    
        if filename != "-":
            self._files.append( filename )
            
    def get_group_names( self, region_arg ):
        
        groups = Groups( self._mdb )
        if region_arg == "EU" :
            urls = groups.get_region_group_urlnames( EU_COUNTRIES )
        elif region_arg == "US" :
            urls = groups.get_region_group_urlnames( [ "USA" ] )
        else:
            urls = groups.get_region_group_urlnames()
            
        return urls
                    
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

        if self._pro_account:
            if self._start_date or self._end_date :
                agg.addRangeMatch( "group.founded_date", self._start_date, self._end_date )
            agg.addProject( { "_id" : 0,
                              "urlname" : "$group.urlname",
                              "members" : "$group.member_count",
                              "founded" : "$group.founded_date" } )
            print( "Using pro search" )
        else:
            if self._start_date or self._end_date :
                agg.addRangeMatch( "group.created", self._start_date, self._end_date )
            agg.addProject( { "_id" : 0,
                              "urlname" : "$group.urlname",
                              "members" : "$group.members",
                              "founded" : "$group.created" } ) 
            print( "Using nopro search")
        if self._sorter:
            agg.addSort( self._sorter)        
        
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg, self._filename, self._format )
        filename = formatter.output( fieldNames= [ "urlname", "members", "founded" ], datemap=[ "founded" ], limit=self._limit )
        
        if self._filename != "-":
            self._files.append( self._filename )
            
    def get_group_totals( self, urls, filename=None ):
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
    
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg, self._filename, self._format )
        filename = formatter.output( fieldNames= [ "year", "group", "event_count", "rsvp_count"], limit=self._limit )
        
        if self._filename != "-":
            self._files.append( self._filename )
        
    def get_events(self, urls, filename=None):
    
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
        
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg, self._filename, self._format )
        filename = formatter.output( fieldNames= [ "group", "name", "rsvp_count", "date" ], datemap=[ "date"], limit=self._limit)

        if self._filename != "-":
            self._files.append( self._filename )
            
    def get_new_members( self, urls, filename=None ):
        '''
        Get all the members of all the groups (urls). Range is join_time.
        '''
        
        agg = Agg( self._mdb.membersCollection())
        

        agg.addMatch({ "batchID"            : self._batchID } )
        
        agg.addUnwind( "$member.chapters" )
        
        agg.addMatch({ "member.chapters.urlname" : { "$in" : urls }} )
        

        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "member.join_time", self._start_date, self._end_date )
            
        agg.addProject( { "_id" : 0,
                          "group"     : "$member.chapters.urlname",
                          "name"      : "$member.member_name",
                          "join_date" : "$member.join_time" } )
        
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg, self._filename, self._format )
        filename = formatter.output( fieldNames= [ "group", "name", "join_date" ], datemap=[ 'join_date'], limit=self._limit)
        
        if self._filename != "-":
            self._files.append( self._filename )
            
    def get_rsvps( self, urls, rsvpbound=0, filename=None):   
        '''
        Lookup RSVPs by user. So for each user collect how many events they RSVPed to.
        '''
        agg = Agg( self._mdb.attendeesCollection())
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "info.event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "info.event_time", self._start_date, self._end_date )
        
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
        
        if self._sorter :
            agg.addSort( self._sorter)
        
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg, self._filename, self._format )
        filename = formatter.output( fieldNames= [ "attendee", "group", "event_count" ], limit=self._limit )

        if self._filename != "-":
            self._files.append( self._filename )
            
    def get_rsvp_by_event(self, urls, filename="rsvp_events"):
        
        agg = Agg( self._mdb.pastEventsCollection())
        
        agg.addMatch({ "batchID"             : self._batchID,
                       "event.group.urlname" : { "$in" : urls }})
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "event.time", self._start_date, self._end_date )
            
        agg.addGroup( { "_id" : "$event.group.urlname",
                        "rsvp_count" : { "$sum" : "$event.yes_rsvp_count" }})

        if self._sorter :
            agg.addSort( self._sorter)
            
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg.aggregate(), self._filename, self._format )
        filename = formatter.output( fieldNames= [ "_id", "rsvp_count" ], limit=self._limit )
        
        if self._filename != "-":
            self._files.append( self._filename )
        
    def get_active_users( self, urls, filename=None ):
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
            
        if filename :
            self._filename = filename

        formatter = CursorFormatter( agg, self._filename, self._format )
        filename = formatter.output( fieldNames= [ "_id", "count", "groups" ], limit=self._limit )

        if self._filename != "-":
            self._files.append( self._filename )
       
 
    def get_totals(self, urls, countries=EU_COUNTRIES, filename=None ):
        '''
        Total number of members
        Total number of groups
        Total number of events
        Total number of RSVPs
        '''
       
        members = Members( self._mdb )

        if countries is None:
            member_count = members.get_all_members().count()
        else:
            member_count = members.get_all_members( { "member.country" : { "$in" : countries }}).count()
        print( "Total members: %i" % member_count )
        
        events = PastEvents( self._mdb )
        
        event_count = events.get_all_events( { "event.group.urlname" : { "$in" : urls }}).count()
        
        print( "Total events: %i" % event_count )
    
        #group_count = groups.

    def output_filename(self):
        return self._filename
    
def convert_direction( arg ):
    
    if arg == "ascending" :
        return pymongo.ASCENDING
    elif arg == "descending" :
        return pymongo.DESCENDING
    else:
        return pymongo.ASCENDING
    
def get_batches( mdb, start, end, limit=None ):
    
    audit = Audit( mdb )
    
    c = CursorFormatter( audit.getCurrentValidBatches( start, end ))
    c.output( [ "batchID" , "end", "start" ], datemap=[ "start", "end" ], limit=limit)

    
def collection_stats( mdb, collection_name ) :
    return mdb.collection_stats( collection_name )
      
def all_collection_stats( mdb ):
    
    for i in mdb.collection_names():
        yield collection_stats( mdb, i )
    
def main( args ):
    
#if __name__ == '__main__':
    
    cmds = [ "grouptotals", "groups", "events", "rsvps", 
            "activeusers", "newmembers", "memberhistory", "rsvphistory",
            "totals", "rsvpevents", "collections" ]

    parser = ArgumentParser( args )
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--format", default="JSON", choices=[ "JSON", "json", "CSV", "csv" ], help="format for output [default: %(default)s]" )
    parser.add_argument( "--prefix", default="<date>", help="prefix for output [default: %(default)s generates datestring]" )
    parser.add_argument( "--output", default="-", help="where to write output [default: %(default)s for stdout]" )
    parser.add_argument( "--stats",  nargs="+", 
                         choices= cmds,
                         help="List of stats to output [default: %(default)s]" )
    parser.add_argument( "--country", nargs="+", default=[ "all"],
                         help="pick a region { all| EU | NORDICS } to report on [default: %(default)s]")
    
    parser.add_argument( "--url", nargs="+",
                         help="pick a URL for a group to report on [default: %(default)s]")

    parser.add_argument( "--start", type=valid_date, help="Starting date range for a query" )
    
    parser.add_argument( "--end", type=valid_date, help="Ending date range for a query" )
    
    parser.add_argument( "--sort", action="append", help="Sort the output using this field")
    
    parser.add_argument( "--direction", action="append", choices=[ "ascending", "descending" ], 
                         default=[], help="Sort direction [default: %(default)s] ")
    
    parser.add_argument( "--limit", type=int, help="Limit the number of output records")
    
    parser.add_argument( "--upload", default=False, action="store_true",  help="upload to gdrive" )
    
    parser.add_argument( "--gdrive_config", default="pydrive_auth.json", help="use this gdrive config [default: %(default)s]" )
    
    parser.add_argument( "--batches", action="store_true", default=False, help="Find all batches since a specific date")
    
    parser.add_argument( "--batchid", type=int, help="Use this batch to satisfy the query")
    
    args = parser.parse_args()
    
    output = args.output
    prefix = args.prefix 
    
    if prefix is None :
        prefix = ""
    
    if prefix == "<date>":
        prefix = datetime.datetime.now().strftime( "%d-%b-%y-%H%M%S" ) + "-"

    if output is None:
        output = "-"
    
    formatter = args.format.lower()
    
    mdb = MUGAlyserMongoDB( uri=args.host )
        
    groups = Groups( mdb )
    
    urls=[]
    
    if args.url :
        urls = args.url
    else:
        if "all" in args.country :
            urls = groups.get_region_group_urlnames()
            countries = None #implies all
        elif "EU" in args.country :
            urls = groups.get_region_group_urlnames( EU_COUNTRIES )
            countries = EU_COUNTRIES
        elif "NORDICS" in args.country :
            urls = groups.get_region_group_urlnames( NORDICS_COUNTRIES )
            countries = NORDICS_COUNTRIES
        else:
            urls = groups.get_region_group_urlnames( args.country )

    if args.start and args.end:
        if args.end < args.start  :
            print( "--end date is before start date ignoring dates")
            args.end = None
            args.start = None
                
    if args.batchid:
        batchID =  args.batchid
    else:
        batchID = None
        
    print( "Processing : %s" % urls )
    analytics = MUG_Analytics( mdb, output, formatter, batchID = batchID, limit=args.limit )
    analytics.setRange(args.start, args.end )
    
    filename = Filename( prefix=prefix, name=args.output, ext=format )
    
    if args.stats is None:
        args.stats = []
        
    sorter=None
    if args.sort :
        sorter = Sorter()
        for i in range( len( args.sort )) :
            if i < len( args.direction )  :
                sorter.add_sort( args.sort[ i ], convert_direction( args.direction[ i ]))
                print( "Sorting on '%s' direction = '%s'" % ( args.sort[ i ],args.direction[ i ]))
            else:
                sorter.add_sort( args.sort[ i ], pymongo.ASCENDING )
                print( "Sorting on '%s' direction = '%s'" % ( args.sort[ i ], "ascending")) 
        analytics.setSort( sorter )
    
    #print( "Current batch ID: %i" % Audit( mdb ).getCurrentBatchID())

    if "grouptotals" in args.stats :
        analytics.get_group_totals( urls, filename=filename( "grouptotals" ))
        
    if "groups" in args.stats :
        analytics.get_groups( urls, filename=filename( "groups" ))
    
    if "newmembers" in args.stats :
        analytics.get_new_members( urls, filename=filename( "members" ))

    if "events" in args.stats:
        analytics.get_events( urls, filename=filename( "events" ))
        
    if "rsvps" in args.stats:
        analytics.get_rsvps( urls, filename=filename( "rsvps" ))
        
    if "activeusers" in args.stats:
        analytics.get_active_users(  urls, filename=filename( "active" ))
        
    if "memberhistory" in args.stats :
        analytics.get_member_history(urls,  filename=filename( "memberhistory"))
        
    if "rsvphistory" in args.stats :
        analytics.get_RSVP_history(urls, filename=filename( "rsvphistory" ))
        
    if "rsvpevents" in args.stats:
        analytics.get_rsvp_by_event(urls, filename=filename( "rsvpevents" ))
        
    if "totals" in args.stats:
        analytics.get_totals( urls, countries=countries, filename=filename( "totals" ))
        
    if args.upload :

        if format == "json" :
            print( "Format is JSON, automatic upload is not supported" )
            print( "Right now we convert uploaded files from CSV to a gsheet automatically")
            print( "This won't work for JSON, so we ignore them for now during upload")
        elif args.output == "-" :
            print( "--output is '-' (stdout), ignoring --upload" )
            print( "Please specify a --output filename to upload files")
        else:
            drive = GDrive()
            drive.get_credentials()
            mugstats_folder = "0By1C8O_N6j4hbUd0cUJfZjAxOUU"
            for i in analytics.files() :
                print( "Uploading: '%s' to google drive" % i )
                ( name, g_id ) = drive.upload_csvFile( mugstats_folder, i )
                print( "Uploaded '%s' to %s' as id: '%s'" % ( i, name, g_id ))

    if args.batches :
        get_batches( mdb, args.start, args.end )
        
    if "collections" in args.stats :
        for i in all_collection_stats(mdb) :
            print( "=====> %s" % i[ "ns"] )
            pprint.pprint( i[ "storageSize"] )
        
if __name__ == '__main__':
    main( sys.argv )
