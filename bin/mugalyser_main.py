#!/usr/bin/env python

'''
mugalyser_main -- Grab MUG Stats and stuff them into a MongoDB Database

@author:     Joe.Drumgoole@mongodb.com

@license:    AFGPL

'''

import sys
from datetime import datetime
from argparse import ArgumentParser
import logging
from traceback import print_exception
import os

import pymongo
import time
from mugalyser.apikey import get_meetup_key
from mugalyser.meetup_api import MeetupAPI

from mugalyser.audit import Audit

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.meetup_writer import MeetupWriter

from mugalyser.version import __version__, __programName__
'''
    11-Oct-2016, 0.8 beta: Bumped version. Changed format of master record in Audit Collection. Changed
    name of groupinfo script to muginfo. Added support for URI format arguments. Added replica set argument.
    
    10-Oct-2016, 0.7 beta:  Added multi-processing. Also put list of canonical mugs into a Python list.
'''


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
        
        parser = ArgumentParser()
        
        #
        # MongoDB Args

        parser.add_argument( '--host', default="mongodb://localhost:27017/MUGS", help='URI to connect to : [default: %(default)s]')

        parser.add_argument( "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument( "-v", "--version", action='version', version="MeetupAPI " + __version__ )
        parser.add_argument( "--wait", default=5, type=int, help='How long to wait between processing the next parallel MUG request [default: %(default)s]')
        parser.add_argument( '--trialrun', action="store_true", default=False, help='Trial run, no updates [default: %(default)s]')
     
        parser.add_argument( '--mugs', nargs="+", help='Process MUGs list list mugs by name [default: %(default)s]')
   
        parser.add_argument( "--pro", default=False, action="store_true", help="use if you have a pro account uses pro API calls")
        parser.add_argument( "--admin", default=False, action="store_true", help="Some calls are only available to admin users")
        parser.add_argument( "--database", default="MUGS", help="Default database name to write to [default: %(default)s]")
        parser.add_argument( '--phases', nargs="+", choices=[ "groups", "members", "attendees", "upcomingevents", "pastevents"], 
                             default=[ "all"], help='execution phases')

        parser.add_argument( '--loglevel', default="INFO", choices=[ "CRITICAL", "ERROR", "WARNING", "INFO",  "DEBUG" ], help='Logging level [default: %(default)s]')
        
        parser.add_argument( '--apikey', default=None, help='Default API key for meetup')
        
        parser.add_argument( '--urlfile', 
                             help="File containing a list of MUG URLs to be used to parse data default: %(default)s]")
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

        if args.pro:
            nopro=False
        else:
            nopro=True
            
        mdb = MUGAlyserMongoDB( args.host )
        
        audit = Audit( mdb )
        
        batchID = audit.startBatch( { "args"    : vars( args ), 
                                      "version" : __programName__ + " " + __version__,
                                      "pro_account" : args.pro },
                                      trial=args.trialrun,
                                      apikey=apikey )

        start = datetime.utcnow()
        logging.info( "Started MUG processing for batch ID: %i", batchID )
        logging.info( "Writing to database : '%s'" % mdb.database().name )
        if nopro:
            logging.info( "Using standard API calls (no pro account API key)")
            if args.urlfile:
                logging.info( "Reading groups from: '%s'", args.urlfile )
                with open( args.urlfile ) as f:
                    mugList = f.read().splitlines()
                
        else:
            logging.info( "Using pro API calls (pro account API key)")
            
        if nopro:
            logging.info( "Processing %i MUG URLS", len( mugList ))
        else:
            mugList = list( MeetupAPI().get_pro_group_names())
        
        writer = MeetupWriter( audit, mdb, mugList,  apikey )
            
        if "all" in args.phases :
            phases = [ "groups", "members", "upcomingevents", "pastevents"]
            if args.admin:
                phases.append( "attendees" )
        else:
            phases = args.phases
        
        if  "groups" in phases :
            logging.info( "processing group info for %i groups: nopro=%s" %( len( mugList), nopro ))
            writer.processGroups( nopro )
            phases.remove( "groups")
        if "members" in phases :
            logging.info( "processing members info for %i groups: nopro=%s" % ( len( mugList), nopro ))
            writer.processMembers( nopro )
            phases.remove( "members")
            
        for i in mugList :
            writer.capture_snapshot( i, nopro, args.admin, phases )
        
        audit.endBatch( batchID )
        end = datetime.utcnow()
    
        elapsed = end - start
            
        logging.info( "MUG processing took %s for BatchID : %i", elapsed, batchID )

    except KeyboardInterrupt:
        print("Keyboard interrupt : Exiting...")
        sys.exit( 2 )

    except pymongo.errors.ServerSelectionTimeoutError, e :
        print( "Failed to connect to MongoDB Server (server timeout): %s" % e )
        sys.exit( 2 )
    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print_exception( exc_type, exc_value, exc_traceback )
        indent = len( __programName__ ) * " "
        sys.stderr.write( __programName__ + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2

        

if __name__ == "__main__":

    sys.exit(main())
