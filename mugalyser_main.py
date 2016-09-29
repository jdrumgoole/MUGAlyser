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

def insertTimestamp( doc, ts=None ):
    if ts :
        doc[ "timestamp" ] = ts
    else:
        doc[ "timestamp" ] = datetime.now()
        
    return doc
  
    
def addTimestamp( name, doc, ts=None ):
    
    tsDoc = { name : doc, "timestamp" : None }
    return insertTimestamp( tsDoc, ts )

def getMugs( mugfile, collection ):
    
    frontCommentRegex = re.compile( '^\s*#' )
    MUGS = []
    
    try:
        with open( mugfile ) as inputFile :
            for line in inputFile:
                if not frontCommentRegex.match( line ):
                    MUGS.append( line.rstrip())
                    
        collection.insert_one( addTimestamp( "MUGS" , MUGS))
        
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


def processMUG( urlName, mdb ):
    
    mlyser = MUGAlyser( MEETUP_API_KEY )
    logging.info( "Processing: '%s'" % urlName )
    group = mlyser.get_group( urlName )
    
    mdb.groupsCollection().insert_one( addTimestamp( "group", group ))
    
    pastEvents = mlyser.get_past_events( urlName )
    
    for i in pastEvents:
        mdb.pastEventsCollection().insert_one( addTimestamp( "event", i ))
        
    upcomingEvents = mlyser.get_upcoming_events( urlName )
    
    for i in upcomingEvents:
        mdb.upcomingEventsCollection().insert_one( addTimestamp( "event", i ))
    members = mlyser.get_members( urlName )
        
    for i in members :
        mdb.membersCollection().insert_one( insertTimestamp( i ))
        
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
        parser.add_argument('--capture', default=False, action='store_true', help="Capture a snapshot of data")
        parser.add_argument( '--mugfile', default="MUGS", help='List of MUGs stored in [default: %(default)s]')
        parser.add_argument( '--mug', default="", help='Process a single MUG [default: %(default)s]')
        
        parser.add_argument( '--loglevel', default="DEBUG", help='Logging level [default: %(default)s]')
        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

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
            
            if args.mug :
                processMUG( args.mug, mdb )
            elif args.mugfile :
                muglist = getMugs( args.mugfile, mdb.auditCollection())
                for i in muglist :
                    processMUG( i, mdb )

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