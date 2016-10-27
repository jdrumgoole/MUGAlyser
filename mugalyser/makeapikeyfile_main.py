'''
Created on 30 Sep 2016

@author: jdrumgoole
'''

import sys
from datetime import datetime
if __name__ == '__main__':
    
    key = sys.argv[ 1 ]
    passwd = sys.argv[ 2 ]

    with open( "apikey_template.py", "r") as infile:
        with open( "apikey.py", "w" ) as output:
            output.write( "# Created: %s\n" % datetime.now())
            for line in infile :
                if line.startswith( "MEETUP_API_KEY"):
                    output.write( "MEETUP_API_KEY=\"%s\"\n" % key )
                elif line.startswith( "MUGALYSER_PASSWD"):
                    output.write( "MUGALYSER_PASSWD=\"%s\"\n" % passwd )
                else:
                    output.write( line )

