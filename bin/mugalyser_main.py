#!/usr/bin/env python

'''
mugalyser_main -- Grab MUG Stats and stuff them into a MongoDB Database

29-May-2017 : Changed program to use --collect argument to allow collection of pro, nopro or all
data. Pro and No Pro data are now stored in seperate collections.

@author:     joe@joedrumgoole.com

@license:    AFGPL

'''

import sys
from datetime import datetime
from argparse import ArgumentParser
import logging
import os

import pymongo

from mugalyser.apikey import get_meetup_key
from mugalyser.meetup_api import MeetupAPI
from mugalyser.audit import Audit
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.meetup_writer import MeetupWriter

__programName__ = "MUGAlyser"
__version__ = "0.8 beta"

DEBUG = 1
TESTRUN = 0
PROFILE = 0

                 
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg  

def LoggingLevel( level="WARN"):

    loglevel = None
    if level == "DEBUG" :
        loglevel = logging.DEBUG 
    elif level == "INFO" :
        loglevel = logging.INFO 
    elif level == "WARNING" :
        loglevel = logging.WARNING 
    elif level == "ERROR" :
        loglevel = logging.ERROR 
    elif level == "CRITICAL" :
        loglevel = logging.CRITICAL
        
    return loglevel  
   
def cleanUp( procs ) :
    for i in procs:
        i.terminate()
        i.join()
             
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv:
        sys.argv.extend( argv )

    try:
        # Setup argument parser
        
        parser = ArgumentParser( description='''
Read data from the Meetup API and write it do a MongoDB database. Each run of this program
creates a new batch of data identified by a batchID. The default database is MUGS. You can change
this by using the --host parameter and specifying a different database in the mongodb URI.
If you use the --pro arguement your API key must be a meetup pro account API key. If not the api
calls to the pro interface will fail.

If you are and adminstrator on the pro account you should use the --admin flag to give you
access to the admin APIs.
''')
        #
        # MongoDB Args

        parser.add_argument( '--host', default="mongodb://localhost:27017/MUGS", help='URI to connect to : [default: %(default)s]')

        parser.add_argument( "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument( "-v", "--version", action='version', version=__programName__ + " " + __version__ )
        parser.add_argument( '--trialrun', action="store_true", default=False, help='Trial run, no updates [default: %(default)s]')
     
        parser.add_argument( '--mugs', nargs="+", help='Process MUGs list list mugs by name [default: %(default)s]')
   
        parser.add_argument( "--collect",  choices=[ "pro", "nopro", "all" ], default="all", help="Use pro API calls, no pro API calls or both")
        parser.add_argument( "--admin", default=False, action="store_true", help="Some calls are only available to admin users")
        parser.add_argument( "--database", default="MUGS", help="Default database name to write to [default: %(default)s]")
        parser.add_argument( '--phases', nargs="+", choices=[ "groups", "members", "attendees", "upcomingevents", "pastevents"], 
                             default=[ "all"], help='execution phases')

        parser.add_argument( '--loglevel', default="INFO", choices=[ "CRITICAL", "ERROR", "WARNING", "INFO",  "DEBUG" ], help='Logging level [default: %(default)s]')
        
        parser.add_argument( '--apikey', default=None, help='Default API key for meetup')
        
        parser.add_argument( '--urlfile', 
                             help="File containing a list of MUG URLs to be used to parse data [ default: %(default)s]")
        # Process arguments
        args = parser.parse_args()
            
        apikey=""
        
        if args.apikey :
            apikey = args.apikey
        else:
            apikey = get_meetup_key()
        
        verbose = args.verbose

        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=format_string, level=LoggingLevel( args.loglevel ))
            
        # Turn off logging for requests
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        if verbose > 0:
            logging.info("Verbose mode on")
            
        if args.urlfile :
            if not os.path.isfile( args.urlfile ):
                print( "No such file --urlfile '%s'" % args.urlfile )
                sys.exit( 1 )
                
        if args.mugs:
            mugList = args.mugs
        else:
            mugList = []

            
        mdb = MUGAlyserMongoDB( args.host )
        
        audit = Audit( mdb )
        
        batchID = audit.start_batch( { "args"    : vars( args ), 
                                      "version" : __programName__ + " " + __version__,
                                      "collect" : args.collect } )

        start = datetime.utcnow()
        logging.info( "Started MUG processing for batch ID: %i", batchID )
        logging.info( "Writing to database : '%s'", mdb.database().name )
        if args.collect in [ "nopro", "all" ] :
            if args.urlfile:
                urlfile = os.path.abspath( args.urlfile )
                logging.info( "Reading groups from: '%s'", urlfile )
                with open( urlfile ) as f:
                    mugList = f.read().splitlines()
            else:
                logging.warning( "No urlfile specified: No groups will be analysed in nopro mode")
                
        elif args.collect == "pro":
            logging.info( "Using pro API calls (pro account API key)")
            
        if args.collect == "pro":
            mugList = list( MeetupAPI().get_pro_group_names())
        
        writer = MeetupWriter( audit, mdb, mugList,  apikey )
            
        if "all" in args.phases :
            phases = [ "groups", "members", "upcomingevents", "pastevents"]
            if args.admin:
                phases.append( "attendees" )
        else:
            phases = args.phases
        
        if  "groups" in phases :
            logging.info( "processing group info for %i groups: collect=%s", len( mugList), args.collect )
            writer.write_groups( args.collect, mugList )
            phases.remove( "groups")
        if "members" in phases :
            logging.info( "processing members info for %i groups: collect=%s", len( mugList), args.collect  )
            writer.write_members( args.collect )
            phases.remove( "members")
            
        for i in mugList :
            writer.capture_snapshot( i, args.admin, phases )
        
        audit.end_batch( batchID )
        end = datetime.utcnow()
    
        elapsed = end - start
            
        logging.info( "MUG processing took %s for BatchID : %i", elapsed, batchID )

    except KeyboardInterrupt:
        print("Keyboard interrupt : Exiting...")
        sys.exit( 2 )

    except pymongo.errors.ServerSelectionTimeoutError, e :
        print( "Failed to connect to MongoDB Server (server timeout): %s" % e )
        sys.exit( 2 )
        

if __name__ == "__main__":

    sys.exit(main())
