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
from apikey import MEETUP_API_KEY

from mongodb import MUGAlyserMongoDB
from mugalyser import MUGAlyser
from traceback import print_exception

__version__ = 0.1

DEBUG = 1
TESTRUN = 0
PROFILE = 0


class AuditDB( object ):
    
    def __init__(self, auditCollection ):
        self._auditCollection = auditCollection
        self._batchID = self._auditCollection.find_one( { "name": "BatchID"})
        
        if self._batchID is None:
            self._batchID = {}
            self._batchID[ "name"] = "BatchID"
            self._batchID[ "ID" ] = 1
        
    def incrementBatchID(self):
        
        self._batchID[ "ID" ] = self._batchID[ "ID" ]  + 1
        self._batchID[ "timestamp" ] = datetime.now()
        self._auditCollection.update( { "name" : "BatchID"}, self._batchID, upsert=True) 
        
    def auditCollection(self):
        return self._auditCollection
    
    def batchID(self):
        return self._batchID[ "ID"]
    
                
def insertTimestamp( doc, ts=None ):
    if ts :
        doc[ "timestamp" ] = ts
    else:
        doc[ "timestamp" ] = datetime.now()
        
    return doc
  

    
def addTimestamp( audit, name, doc, ts=None ):
    
    tsDoc = { name : doc, "timestamp" : None, "batchID": audit.batchID()}
    return insertTimestamp( tsDoc, ts )

def getMugs( mugfile, audit ):
    
    frontCommentRegex = re.compile( '^\s*#' )
    MUGS = []
    
    try:
        with open( mugfile ) as inputFile :
            for line in inputFile:
                if not frontCommentRegex.match( line ):
                    MUGS.append( line.rstrip())
                    
        audit.auditCollection().insert_one( addTimestamp( audit, "MUGS" , MUGS))
        
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


def processMUG( urlName, mdb, audit ):
    
    mlyser = MUGAlyser( MEETUP_API_KEY )
    logging.info( "Processing: '%s'" % urlName )
    
    group = mlyser.get_group( urlName )
    
    mdb.groupsCollection().insert_one( addTimestamp( audit, "group", group))
    
    pastEvents = mlyser.get_past_events( urlName )
    
    for i in pastEvents:
        mdb.pastEventsCollection().insert_one( addTimestamp( audit, "event", i ))
        
    upcomingEvents = mlyser.get_upcoming_events( urlName )
    
    for i in upcomingEvents:
        mdb.upcomingEventsCollection().insert_one( addTimestamp( audit, "event", i ))
    members = mlyser.get_members( urlName )
        
    for i in members :
        #print( "Adding: %s" % i[ 'name'] )
        mdb.membersCollection().insert_one( addTimestamp(  audit, "member",  i ))
        
    return group

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_version_message = '%%(prog)s %s' % (program_version )
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
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
        parser.add_argument( '--admindb', default="admin", help="Admin database used for authentication [default: %(default)s]" )
        parser.add_argument( '--ssl', default=False, action="store_true", help='use SSL for connections')

        #
        # Program args
        #
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('--capture', default=True, action='store_true', help="Capture a snapshot of data")
        parser.add_argument( '--mugfile', help='List of MUGs stored in [default: %(default)s]')
        parser.add_argument( '--mug', help='Process a single MUG [default: %(default)s]')
        
        parser.add_argument( '--loglevel', default="INFO", help='Logging level [default: %(default)s]')
        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        
        root = logging.getLogger()
        root.setLevel(logging.INFO)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
        

        
        if verbose > 0:
            logging.info("Verbose mode on")
            
        if args.capture :
            mdb = MUGAlyserMongoDB( args.host, args.port, args.database, args.username, args.password, args.ssl, args.admindb )
            mdb.connect()
            

            audit = AuditDB( mdb.auditCollection())
            audit.incrementBatchID()
            if args.mug :
                processMUG( args.mug, mdb, audit )
            elif args.mugfile :
                muglist = getMugs( args.mugfile, audit )
                for i in muglist :
                    processMUG( i, mdb, audit )

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print_exception( exc_type, exc_value, exc_traceback )
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2

if __name__ == "__main__":

    sys.exit(main())