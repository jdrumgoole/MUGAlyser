'''
Created on 30 Sep 2016

@author: jdrumgoole
'''

import sys
from datetime import datetime
if __name__ == '__main__':
    
    key = sys.argv[ 1 ]
    with open( "apikey.py", "w") as keyfile:
        keyfile.write( "# Created: %s\n" % datetime.now())
        keyfile.write( "MEETUP_API_KEY=\"%s\"" % key )