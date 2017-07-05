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
from mugalyser.version import __programName__, __version__
from mugalyser.logger import Logger
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

        parser.add_argument( "-v", "--version", action='version', version=__programName__ + " " + __version__ )
        parser.add_argument( '--trialrun', action="store_true", default=False, help='Trial run, no updates [default: %(default)s]')
     
        parser.add_argument( '--mugs', nargs="+", default=[], help='Process MUGs list list mugs by name [default: %(default)s]')
   
        parser.add_argument( "--collect",  choices=[ "pro", "nopro", "all" ], default="all", help="Use pro API calls, no pro API calls or both")
        parser.add_argument( "--noadmin", default=True, action="store_false", help="Some calls are only available to admin users, use this if you are not an admin")
        parser.add_argument( "--database", default="MUGS", help="Default database name to write to [default: %(default)s]")
        parser.add_argument( '--phases', nargs="+", choices=[ "groups", "members", "attendees", "upcomingevents", "pastevents"], 
                             default=[ "all"], help='execution phases')

        parser.add_argument( '--loglevel', default="INFO", choices=[ "CRITICAL", "ERROR", "WARNING", "INFO",  "DEBUG" ], help='Logging level [default: %(default)s]')
        
        parser.add_argument( '--apikey', default=None, help='Default API key for meetup')
        
        parser.add_argument( "--batchname", default= "test " + __programName__, help="Batch name used in creating audit batches")
        parser.add_argument( '--urlfile', 
                             help="File containing a list of MUG URLs to be used to parse data [ default: %(default)s]")
        # Process arguments
        args = parser.parse_args()
            
        apikey=""
        
        if args.apikey :
            apikey = args.apikey
        else:
            apikey = get_meetup_key()

        mugalyser_logger = Logger( __programName__ )
        mugalyser_logger.add_stream_handler()
        mugalyser_logger.add_file_handler( "mugalyser.log" )
        
        logger = mugalyser_logger.log()
        
        # Turn off logging for requests
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
            
        mdb = MUGAlyserMongoDB( args.host )
        
        audit = Audit( mdb )
        
        batchID = audit.start_batch( { "args"   : vars( args ), 
                                      "version" : __programName__ + " " + __version__,
                                      "name"    : args.batchname,
                                      "collect" : args.collect } )

        start = datetime.utcnow()
        logger.info( "Started MUG processing for batch ID: %i", batchID )
        logger.info( "Writing to database : '%s'", mdb.database().name )
        
        if args.collect in [ "pro", "all"]:
            '''
            Use the pro API.
            '''
            logger.info( "Using pro API calls (pro account API key)")
            mugList = list( MeetupAPI( apikey ).get_pro_group_names())
        elif args.collect in [ "nopro" ] :
            if args.urlfile:
                urlfile = os.path.abspath( args.urlfile )
                logger.info( "Reading groups from: '%s'", urlfile )
                with open( urlfile ) as f:
                    mugList = f.read().splitlines()
            else:
                mugList = args.mugs

        if not args.noadmin:
            logger.info( "Using admin account")

        writer = MeetupWriter( apikey, batchID, mdb )
            
        if "all" in args.phases :
            phases = [ "groups", "members", "upcomingevents", "pastevents"]
            if args.noadmin:
                logger.info( "--noadmin : we will not collect attendee info")
            else:
                phases.append( "attendees" )
                logger.info( "No --admin : we will not collect attendee info")
        else:
            phases = args.phases
            
        logger.info( "Processing phases: %s", phases )
        
        if  "groups" in phases :
            logger.info( "processing group info for %i groups: collect=%s", len( mugList), args.collect )
            writer.write_groups( args.collect, mugList )
            phases.remove( "groups")
        if "members" in phases :
            logger.info( "processing members info for %i groups: collect=%s", len( mugList), args.collect  )
            writer.write_members( args.collect, mugList )
            phases.remove( "members")
            
        for i in mugList :
            writer.capture_snapshot( i, not args.noadmin, phases )
        
        audit.end_batch( batchID )
        end = datetime.utcnow()
    
        elapsed = end - start
            
        logger.info( "MUG processing took %s for BatchID : %i", elapsed, batchID )

    except KeyboardInterrupt:
        print("Keyboard interrupt : Exiting...")
        sys.exit( 2 )

    except pymongo.errors.ServerSelectionTimeoutError, e :
        print( "Failed to connect to MongoDB Server (server timeout): %s" % e )
        sys.exit( 2 )
        

if __name__ == "__main__":

    sys.exit(main())
