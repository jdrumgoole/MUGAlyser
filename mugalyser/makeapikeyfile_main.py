'''
Created on 30 Sep 2016

@author: jdrumgoole
'''

import sys
from argparse import ArgumentParser

from datetime import datetime

if __name__ == '__main__':
    
    
    parser = ArgumentParser()
    parser.add_argument( "-a", "--apikey", default="", help="Meetup API key")
    
    args = parser.parse_args()
    
    apikey = args.apikey
    
    if ( apikey == "" ) :
        print( "Warning no argument to --apikey, have you defined MEETUP_API_KEY in the environment?")
        print( "Goto https://secure.meetup.com/meetup_api/key/ to get an API key for meetup.com")

    with open( "apikey_template.py", "r") as infile:
        with open( "apikey.py", "w" ) as output:
            output.write( "# Created: %s\n" % datetime.now())
            for line in infile :
                if line.startswith( "MEETUP_API_KEY"):
                    output.write( "MEETUP_API_KEY=\"%s\"\n" % apikey )
                else:
                    output.write( line )
                    
    if apikey == "" :
        sys.exit( 2 )
    else:
        sys.exit( 0 )

