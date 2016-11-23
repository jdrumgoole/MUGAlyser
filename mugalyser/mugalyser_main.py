#!/usr/local/bin/python2.7
# encoding: utf-8
'''
mugalyser_main -- Grab MUG Stats and stuff them into a MongoDB Database

@author:     Joe.Drumgoole@mongodb.com

@license:    AFGPL

'''

import sys
import os
import re
from datetime import datetime
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import logging
from traceback import print_exception

import pymongo
import time

from meetup_api import MeetupAPI

try:
    from apikey import get_meetup_key
except ImportError,e :
    print( "Failed to import apikey: have you run makeapikeyfile_main.py <APIKEY> : %s" % e )
    sys.exit( 2 )

from audit import Audit

from mongodb import MUGAlyserMongoDB
from meetup_writer import MeetupWriter

from version import __version__, __programName__
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

def setLoggingLevel(  logger, level="WARN"):

    if level == "DEBUG" :
        logger.setLevel( logging.DEBUG )
    elif level == "INFO" :
        logger.setLevel( logging.INFO )
    elif level == "WARNING" :
        logger.setLevel( logging.WARNING )
    elif level == "ERROR" :
        logger.setLevel( logging.ERROR )
    elif level == "CRITICAL" :
        logger.setLevel( logging.CRITICAL )
        
    return logger  
   
def cleanUp( procs ) :
    for i in procs:
        i.terminate()
        i.join()
             
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_shortdesc = "A program to read data from the Meetup API into MongoDB"
    program_license = '''%s

  Licensed under the AGPL
  https://www.gnu.org/licenses/agpl-3.0.en.html

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc )

    try:
        # Setup argument parser
        
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        
        #
        # MongoDB Args
        parser.add_argument( '--database', default="MUGS", help='specify the database name [default: %(default)s]')
        parser.add_argument( '--url', default="mongodb://localhost:27017", help='URI to connect to : [default: %(default)s]')

        parser.add_argument( "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument( "-v", "--version", action='version', version="MeetupAPI " + __version__ )
        parser.add_argument( "--wait", default=5, type=int, help='How long to wait between processing the next parallel MUG request [default: %(default)s]')
        parser.add_argument( '--trialrun', action="store_true", default=False, help='Trial run, no updates [default: %(default)s]')
     
        parser.add_argument( '--mugs', nargs="+", default=[ "all" ], help='Process MUGs list list mugs by name [default: %(default)s]')
   
        parser.add_argument( '--phases', nargs="+", choices=[ "groups", "members", "attendees", "upcomingevents", "pastevents"], 
                             default=[ "all"], help='execution phases')

        parser.add_argument( '--loglevel', default="INFO", choices=[ "CRITICAL", "ERROR", "WARNING", "INFO",  "DEBUG" ], help='Logging level [default: %(default)s]')
        
        parser.add_argument( '--apikey', default=None, help='Default API key for meetup')
        
        # Process arguments
        args = parser.parse_args()
            
        apikey=""
        
        if args.apikey :
            apikey = args.apikey
        else:
            apikey = get_meetup_key()
        
        verbose = args.verbose

        logger = logging.getLogger( __programName__ )
        setLoggingLevel( logger, args.loglevel )

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        #print( "logging to: %s" % __programName__ )
        if verbose > 0:
            logger.info("Verbose mode on")
            
        mugList = []

        mdb = MUGAlyserMongoDB( args.url )

        audit = Audit( mdb )
        
        batchID = audit.startBatch( args.trialrun,
                                    { "args"    : vars( args ), 
                                      "version" : program_name + " " + __version__ },
                                   apikey )

        start = datetime.utcnow()
        logger.info( "Started MUG processing for batch ID: %i", batchID )
        reader = MeetupAPI( apikey )

            
        writer = MeetupWriter( mdb, reader )
        if "all" in args.mugs :
            writer.capture_complete_snapshot()
        else:
            mugList.extend( args.mugs )
            
            if "all" in args.phases :
                phases = [ "groups", "members", "attendees", "upcomingevents", "pastevents"]
            else:
                phases = args.phases
            
            for i in mugList :
                logger.info( "Getting data for: %s", i )
                writer.capture_snapshot( i, phases )
                time.sleep( args.wait )
        
        audit.endBatch( batchID )
        end = datetime.utcnow()
    
        elapsed = end - start
            
        logger.info( "MUG processing took %s for BatchID : %i", elapsed, batchID )

    except KeyboardInterrupt:
        print("Keyboard interrupt : Exiting...")
        sys.exit( 2 )

    except pymongo.errors.ServerSelectionTimeoutError, e :
        print( "Failed to connect to MongoDB Server (server timeout): %s" % e )
        sys.exit( 2 )
    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print_exception( exc_type, exc_value, exc_traceback )
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2

        

if __name__ == "__main__":

    sys.exit(main())
