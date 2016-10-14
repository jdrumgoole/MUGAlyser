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
import multiprocessing
import time

from batchwriter import BatchWriter

from requests import HTTPError
from pydoc import Doc

try:
    from apikey import MEETUP_API_KEY
except ImportError,e :
    print( "Failed to import apikey: have you run makeapikeyfile_main.py <APIKEY> : %s" % e )
    sys.exit( 2 )

from audit import AuditDB

from mongodb import MUGAlyserMongoDB
from mugalyser import MUGAlyser
from mugs import MUGS

from version import __version__, __programName__
'''
    11-Oct-2016, 0.8 beta: Bumped version. Changed format of master record in Audit Collection. Changed
    name of groupinfo script to muginfo. Added support for URI format arguments. Added replica set argument.
    
    10-Oct-2016, 0.7 beta:  Added multi-processing. Also put list of canonical mugs into a Python list.
'''


DEBUG = 1
TESTRUN = 0
PROFILE = 0


def getMugs( muglist, mugfile ):
    
    frontCommentRegex = re.compile( '^\s*#' )
    
    try:
        with open( mugfile ) as inputFile :
            for line in inputFile:
                if not frontCommentRegex.match( line ):
                    muglist.append( line.rstrip())
        
        return muglist 
        
    except IOError:
        print( "Can't open file: '%s'" % mugfile )
        sys.exit( 2 )
    
    return MUGS
                 
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def mergeEvents( writer ):
    for attendee, event in writer:
        doc = { "attendee" : attendee,
                "event" : event }
        yield doc 
        
def processAttendees( args, groups ):
    
    mdb = MUGAlyserMongoDB( args.host, args.port, args.database, args.replset, args.username, args.password, args.ssl, args.admindb )

    mlyser = MUGAlyser( MEETUP_API_KEY )
    
    bw = BatchWriter( mdb.attendeeCollection(), mdb.auditCollection())
    
    audit= AuditDB( mdb )
    
    writer = mlyser.get_attendees( groups, items=100)
    
    newWriter = mergeEvents( writer )
    
    bw.bulkWrite( newWriter, audit.addTimestamp, "info")
    
    
def processMUG( args, urlName ):
    
    if args.trialrun:
        return 
    
    mdb = MUGAlyserMongoDB( args.host, args.port, args.database, args.replset, args.username, args.password, args.ssl, args.admindb )
    audit = AuditDB( mdb )
    mlyser = MUGAlyser( MEETUP_API_KEY )
    #logging.info( "Processing: '%s'" % urlName )
    try :
        group = mlyser.get_group( urlName )
        
        mdb.groupsCollection().insert_one( audit.addTimestamp( "group", group))
        
        pastEvents = mlyser.get_past_events( urlName )
        
        for i in pastEvents:
            mdb.pastEventsCollection().insert_one( audit.addTimestamp(  "event", i ))
            
        upcomingEvents = mlyser.get_upcoming_events( urlName )
        
        for i in upcomingEvents:
            mdb.upcomingEventsCollection().insert_one( audit.addTimestamp( "event", i ))
        members = mlyser.get_members( urlName )
            
        for i in members :
            #print( "Adding: %s" % i[ 'name'] )
            mdb.membersCollection().insert_one( audit.addTimestamp( "member",  i ))
        
        return group
    except HTTPError, e :
        logging.fatal( "Stopped processing: %s" % urlName )
        sys.exit( 2 )
        

def setLoggingLevel(  logger, level="WARN"):
    
    if level == "DEBUG" :
        logger.SetLevel( logging.DEBUG )
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

  Licensed under the AFGPL
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
        parser.add_argument( '--host', default="localhost", help='hostname [default: %(default)s]')
        parser.add_argument( '--port', default="27017", help='port name [default: %(default)s]', type=int)
        parser.add_argument( '--username', default=None, help='username to login to database')
        parser.add_argument( '--password', default=None, help='password to login to database')
        parser.add_argument( '--replset', default="", help='replica set to use [default: %(default)s]' )
        parser.add_argument( '--admindb', default="admin", help="Admin database used for authentication [default: %(default)s]" )
        parser.add_argument( '--ssl', default=False, action="store_true", help='use SSL for connections')
        parser.add_argument( '--multi', default=False, action="store_true", help='use multi-processing')
        #
        # Program args
        #
        parser.add_argument( "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument( "-v", "--version", action='version', version="MUGAlyser " + __version__ )
        parser.add_argument( "--wait", default=5, type=int, help='How long to wait between processing the next parallel MUG request [default: %(default)s]')
        parser.add_argument( '--trialrun', action="store_true", default=False, help='Trial run, no updates [default: %(default)s]')
     
        parser.add_argument( '--mugs', nargs="+", default=[], help='Process MUGs list list mugs by name or use "all"')
   
        parser.add_argument( '--attendees', nargs="+", default=["DUblinMUG"], help='Capture attendees for these groups')

        parser.add_argument( '--loglevel', default="INFO", help='Logging level [default: %(default)s]')
        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        root = logging.getLogger()
        setLoggingLevel( root, args.loglevel )

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
        
        if verbose > 0:
            logging.info("Verbose mode on")
            
        mugList = []
        
        if len( args.mugs ) > 0 :
            if args.mug[0]  == "all":
                mugList = MUGS.keys()
            else:
                mugList.append( args.mug )

                mdb = MUGAlyserMongoDB( args.host, args.port, args.database, args.replset, args.username, args.password, args.ssl, args.admindb )
            
                audit = AuditDB( mdb )
                audit.startBatch( args.trialrun,
                                 { "args"    : vars( args ), 
                                   "MUGS"    : mugList, 
                                   "version" : program_name + " " + __version__ })
        
                start = datetime.utcnow()
                for i in mugList :

                    if args.multi:
                        procs = []
                        p = multiprocessing.Process(target=processMUG, args=(args, i, ))
                        procs.append( p )
                        logging.info( "Getting data for : %s (via subprocess)" % i )
                        p.start()
                        time.sleep( args.wait )
                    else:
                        logging.info( "Getting data for: %s" % i )
                        processMUG( args, i )
                        time.sleep( args.wait )
                
                    audit.endBatch()
                    end = datetime.utcnow()
            
                    elapsed = end - start
                    logging.info( "MUG processing took: %s", elapsed )
                    
        if len( args.attendees ) > 0 :
            if args.attendees[ 0 ] == "all" :
                groups = MUGS.keys()
            else:
                groups = args.attendees
            
            mdb = MUGAlyserMongoDB( args.host, args.port, args.database, args.replset, args.username, args.password, args.ssl, args.admindb )
            
            audit = AuditDB( mdb )
            audit.startBatch( args.trialrun,
                              { "args"         : vars( args ), 
                                "attendees"    : groups, 
                                "version"      : program_name + " " + __version__ } )
            start = datetime.utcnow()
            logging.info( "Processing attendees")
            processAttendees( args, groups )
            audit.endBatch()

            end = datetime.utcnow()
            
            elapsed = end - start
            logging.info( "Attendee processing took: %s", elapsed )

    except KeyboardInterrupt:
        if args.multi:
            logging.info( "Cleaning up subprocesses..")
            cleanUp(procs)
        return 0
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
