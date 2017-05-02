'''
Created on 30 Sep 2016

@author: jdrumgoole
'''

import sys
import os
from argparse import ArgumentParser

from datetime import datetime

if __name__ == '__main__':
    
    
    parser = ArgumentParser()
    parser.add_argument( "-a", "--apikey", default="", help="Meetup API key")
    
    args = parser.parse_args()
    
    root = os.getenv( "MROOT")
    
    if root is None:
        print( "You need to define MROOT to point to the github project root (MUGAlyser dir)")
        sys.exit( 2 )
    else:
        root = os.path.join( root, "mugalyser")
        
    apikey = args.apikey
    
    if ( apikey == "" ) :
        print( "Warning no argument to --apikey, have you defined MEETUP_API_KEY in the environment?")
        print( "Goto https://secure.meetup.com/meetup_api/key/ to get an API key for meetup.com")
        
    input_path = os.path.join( root, "apikey_template.py" )
    output_path = os.path.join( root, "apikey.py" )
    with open( input_path, "r") as infile:
        with open( output_path, "w" ) as outfile:
            outfile.write( "# Created: %s\n" % datetime.now())
            for line in infile :
                if line.startswith( "MEETUP_API_KEY"):
                    outfile.write( "MEETUP_API_KEY=\"%s\"\n" % apikey )
                    print( "%s -> %s" % ( apikey, output_path ))
                else:
                    outfile.write( line )
        
    if apikey == "" :
        sys.exit( 2 )
    else:
        sys.exit( 0 )

