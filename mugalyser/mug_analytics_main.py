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


from mongodb_utils.agg import Sorter
from mugalyser.analytics import MUG_Analytics, Filename
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from mugalyser.groups import EU_COUNTRIES, NORDICS_COUNTRIES, Groups
from mugalyser.members import Members
    
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

def convert_direction( arg ):
    
    if arg == "ascending" :
        return pymongo.ASCENDING
    elif arg == "descending" :
        return pymongo.DESCENDING
    else:
        return pymongo.ASCENDING
    
def get_batches( mdb, start, end ):
    
    audit = Audit( mdb )
    
    for i in audit.get_valid_batches( start, end ):
        print( "BatchID :%i End : %s " % ( i[ "batchID"], i[ "end"].strftime( "%d-%b-%Y %H:%M.%S")))
    #c.output( [ "batchID" , "end", "start" ], datemap=[ "start", "end" ], limit=limit)

    
def collection_stats( mdb, collection_name ) :
    return mdb.collection_stats( collection_name )
      
def all_collection_stats( mdb ):
    
    for i in mdb.collection_names():
        yield collection_stats( mdb, i )
    
def main( argv ):
    
#if __name__ == '__main__':
    
    cmds = [ "grouptotals", "groups", "pastevents", "rsvps", 
            "activeusers", "newmembers", "memberhistory", "rsvphistory",
            "totalevents", "totals", "rsvpevents", "collections", "upcomingevents", "members", "organisers" ]

    parser = ArgumentParser( argv )
        
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
    
    parser.add_argument( "--groups", default=False, action="store_true", help="list all groups (can be filtered by country)")

    parser.add_argument( "--start", type=valid_date, help="Starting date range for a query" )
    
    parser.add_argument( "--end", type=valid_date, help="Ending date range for a query" )
    
    parser.add_argument( "--sort", action="append", help="Sort the output using this field")
    
    parser.add_argument( "--direction", action="append", choices=[ "ascending", "descending" ], 
                         default=[], help="Sort direction [default: %(default)s] ")
    
    parser.add_argument( "--limit", type=int, help="Limit the number of output records")
    
    parser.add_argument( "--upload", default=False, action="store_true",  help="upload to gdrive" )
    
    parser.add_argument( "--gdrive_config", default="pydrive_auth.json", help="use this gdrive config [default: %(default)s]" )
    
    parser.add_argument( "--batches", action="store_true", default=False, help="Find all batches since a specific date")
    
    parser.add_argument( "--createview", action="store_true", default=False, help="Make a view from the agg pipeline")
    
    parser.add_argument( "--batchid", type=int, help="Use this batch to satisfy the query")
    
    args = parser.parse_args()
    
    output = args.output
    prefix = args.prefix 
    
    if prefix is None :
        prefix = ""
    
    if prefix == "<date>":
        prefix = datetime.datetime.now().strftime( "%d-%b-%y-%H%M%S" )

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

    if args.groups:
        for i in urls:
            print( i )
        
    if args.start and args.end:
        if args.end < args.start  :
            print( "--end date is before start date ignoring dates")
            args.end = None
            args.start = None
                
    if args.batchid:
        batchID =  args.batchid
    else:
        batchID = None
        
    #print( "Processing : %i urls" % len( urls ))
    analytics = MUG_Analytics( mdb, formatter, batchID = batchID, limit=args.limit, view=args.createview )
    analytics.setRange(args.start, args.end )
    
    filename = Filename( prefix=prefix, name=output, suffix="", ext=formatter)
    
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
        analytics.get_group_totals( urls, filename=filename.suffix( "grouptotals" ))
        
    if "groups" in args.stats :
        analytics.get_groups( urls, filename=filename.suffix( "groups" ))
    
    if "newmembers" in args.stats :
        analytics.get_new_members( urls, filename=filename.suffix( "members" ))

    if "pastevents" in args.stats:
        analytics.get_events( urls, when="past", filename=filename.suffix( "events" ))
        
    if "upcomingevents" in args.stats :
        analytics.get_events( urls, when="upcoming", filename=filename.suffix( "events" ))
        
    if "rsvps" in args.stats:
        analytics.get_rsvps( urls, filename=filename.suffix( "rsvps" ))
        
    if "activeusers" in args.stats:
        analytics.get_active_users(  urls, filename=filename.suffix( "active" ))
        
    if "memberhistory" in args.stats :
        analytics.get_member_history(urls,  filename=filename.suffix( "memberhistory"))
        
    if "organisers" in args.stats :
        analytics.get_organisers(urls,  filename=filename.suffix( "organisers"))
        
    if "rsvphistory" in args.stats :
        analytics.get_RSVP_history(urls, filename=filename.suffix( "rsvphistory" ))
        
    if "rsvpevents" in args.stats:
        analytics.get_rsvp_by_event(urls, filename=filename.suffix( "rsvpevents" ))
        
    if "totalevents" in args.stats :
        analytics.get_total_events(urls, filename=filename.suffix( "totalevents" ))
        
    if "members" in args.stats :
        analytics.get_members(urls, filename=filename.suffix( "members" ))
        
    if "totals" in args.stats:
        analytics.get_totals( urls, countries=countries )
        
    if args.upload :

        if format == "json" :
            print( "Format is JSON, automatic upload is not supported" )
            print( "Right now we convert uploaded files from CSV to a gsheet automatically")
            print( "This won't work for JSON, so we ignore them for now during upload")
        elif output == "-" :
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
    main( sys.argv[1:] )
