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
from mugalyser.sfdc_analytics import SFDC_Analytics, Filename
    
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
 

def convert_direction( arg ):
    
    if arg == "ascending" :
        return pymongo.ASCENDING
    elif arg == "descending" :
        return pymongo.DESCENDING
    else:
        return pymongo.ASCENDING
    
    
def main( argv ):
    
#if __name__ == '__main__':
    
    cmds = [ "jobs" ]

    parser = ArgumentParser( argv )
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/SFDC", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--format", default="JSON", choices=[ "JSON", "json", "CSV", "csv" ], help="format for output [default: %(default)s]" )
    parser.add_argument( "--prefix", default="<date>", help="prefix for output [default: %(default)s generates datestring]" )
    parser.add_argument( "--output", default="-", help="where to write output [default: %(default)s for stdout]" )
    parser.add_argument( "--stats",  nargs="+", 
                         choices= cmds,
                         help="List of stats to output [default: %(default)s]" )

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
    
    client = pymongo.MongoClient( host=args.host )
    db = client[ "SFDC" ]
    collection = db[ "contacts" ]
        
    if args.start and args.end:
        if args.end < args.start  :
            print( "--end date is before start date ignoring dates")
            args.end = None
            args.start = None
                
        
    #print( "Processing : %i urls" % len( urls ))
    analytics = SFDC_Analytics( collection, formatter, limit=args.limit, view=args.createview )
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
    
    if "jobs" in args.stats :
        analytics.get_job_groups( filename=filename.suffix( "jobs" ))
  
        
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
        
if __name__ == '__main__':
    main( sys.argv[1:] )
