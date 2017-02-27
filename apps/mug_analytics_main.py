'''
Created on 28 Dec 2016

@author: jdrumgoole
'''
from argparse import ArgumentParser
from mugalyser.agg import Agg, Sorter
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from mugalyser.groups import EU_COUNTRIES, NORDICS_COUNTRIES, Groups
import pprint
import pymongo
import csv
import sys
from datetime import datetime
from mugalyser.members import Members
from dateutil.parser import parse
from pydrive import auth
from pydrive.drive import GoogleDrive

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


#
# analytics functions
#

class MUG_Analytics( object ):
    
    def make_filename( self, fileroot, fmt, suffix=None ):
        
        filename = None
        
        if fileroot == "-" :
            return fileroot
        else:
            
            if suffix:
                filename = fileroot + suffix
            else:
                filename = fileroot
                
            if fmt == "CSV" :
                return filename + ".csv"
            else:
                return filename + ".json"
            
    def printCursor( self, c, filename, fmt, fieldnames=None  ):
    
        if fmt == "CSV" :
            self.printCSVCursor( c, filename, fieldnames )
        else:
            self.printJSONCursor( c, filename )
            
        self._files.append( filename )
            
    def files(self):
        return self._files
    
    @contextlib.contextmanager
    def smart_open(self, filename=None):
        if filename and filename != '-':
            fh = open(filename, 'wb' )
        else: 
            fh = sys.stdout
    
        try:
            yield fh
        finally:
            if fh is not sys.stdout:
                fh.close()
                
    def printCSVCursor( self, c, filename, fieldnames ):
            
        if filename !="-" :
            print( "Writing : '%s'" % filename )
        with self.smart_open( filename ) as output :
            writer = csv.DictWriter( output, fieldnames = fieldnames)
            writer.writeheader()
            for i in c:
                x={}
                for k,v in i.items():
                    if type( v ) is unicode :
                        x[ k ] = v
                    else:
                        x[ k ] = str( v ).encode( 'utf8')
                    
                writer.writerow( {k:v.encode('utf8') for k,v in x.items()} ) 
    
    
    def printJSONCursor( self, c, filename ):
        count = 0 
        if filename !="-" :
            print( "Writing : '%s'" % filename )
        with self.smart_open( filename ) as output:
            for i in c :
                pprint.pprint(i, output )
                count = count + 1
            output.write( "Total records: %i\n" % count )

    
    def __init__(self, mdb, format, start_date, end_date, fileroot ):
        self._mdb = mdb
        audit = Audit( mdb )
    
        self._batchID = audit.getCurrentValidBatchID()
        self._start_date = start_date
        self._end_date = end_date
        self._format = format
        self._fileroot = fileroot
        self._files = []
        
    def getMembers( self, urls, filename=None ):
        
        agg = Agg( self._mdb.groupsCollection())
        
        agg.addMatch({ "batchID"       : self._batchID,
                       "group.urlname" : { "$in" : urls }} )
         
        agg.addProject(  { "_id" : 0, 
                           "urlname" : "$group.urlname", 
                           "country" : "$group.country",
                           "member_count" : "$group.member_count" })
        agg.addSort( Sorter("member_count", pymongo.DESCENDING ))
        cursor = agg.aggregate()
        
        filename = self.make_filename( self._root, self._format,  filename )
        self.printCursor( cursor, filename, self._format, fieldnames= [ "urlname", "country", "member_count"] )
        
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
        
        cursor = agg.aggregate()
        
        filename = self.make_filename( self._root, self._format,  filename )
        
        self.printCursor( cursor, filename, fmt=self._format, fieldnames=[ "year", "total_rsvp", "total_events"] )
    
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
        cursor = agg.aggregate()
        
        filename = self.make_filename( self._root, self._format,  filename )
        self.printCursor( cursor, filename, self._format, fieldnames=[ "urlname", "founded" ] )
    
        
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
    
        cursor = agg.aggregate()
        
        filename = self.make_filename( self._root, self._format,  filename )
        
        self.printCursor( addCountry( self._mdb, cursor ), filename, self._format, fieldnames=[  "year", "group", "country", "event_count", "rsvp_count" ] ) 
    
        
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
        cursor = agg.aggregate()
        
        filename = self.make_filename( self._root, self._format,  filename )
            
        self.printCursor( cursor, filename, self._format, fieldnames=[ "group", "name", "rsvp_count", "date" ] ) #"day", "month", "year" ] )
        
    def get_new( self, urls, rsvpbound=0, filename=None ):
        pass
    
    def get_rsvps( self, region, rsvpbound=0, filename=None):   
    
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
        cursor = agg.aggregate()
        
        filename = self.make_filename( self._root, self._format,  filename )
        
        self.printCursor( cursor, filename, self._format, fieldnames=[ "attendee", "group", "event_count"])
    
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
    
        cursor = agg.aggregate()
        
        filename = self.make_filename( self._root, self._format,  filename )
            
        self.printCursor( cursor, filename, self._format, fieldnames=[ "_id", "count", "groups"])
    
if __name__ == '__main__':
    
    cmds = [ "meetuptotals", "grouptotals", "groups",  "members", "events", "rsvps", "active", "new" ]
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--format", default="JSON", choices=[ "JSON", "CSV" ], help="format for output [default: %(default)s]" )
    parser.add_argument( "--fileroot", default="-", help="filename root for output [default: %(default)s]" )
    parser.add_argument( "--stats",  nargs="+", default=[ "meetups" ], 
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
    
    fileroot = args.fileroot
    
    if fileroot is None:
        fileroot = "-"
    
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

    analytics = MUG_Analytics( mdb, args.format, from_date, to_date, fileroot )
    
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

    if "new" in args.stats :
        analytics.get_new( urls, filename="new" )
        
    if args.upload :
        gauth = auth.GoogleAuth()
        gauth.LoadClientConfigFile( args.gdrive_config )
        
        drive = GoogleDrive(gauth)
        
        for i in analytics.files() :
            file1 = drive.CreateFile({'title': i})  # Create GoogleDriveFile instance with title 'Hello.txt'.
            file1.SetContentFile( i ) # Set content of the file from given string.
            file1.Upload()