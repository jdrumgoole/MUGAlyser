'''
Created on 17 Nov 2016

@author: jdrumgoole
'''

import sys
import pprint

from argparse import ArgumentParser
from mugalyser import MUGAlyser

try:
    from apikey import get_meetup_key
except ImportError,e :
    print( "Failed to import apikey: have you run makeapikeyfile_main.py <APIKEY> : %s" % e )
    sys.exit( 2 )

if __name__ == '__main__':
    
    
    m = MUGAlyser()
    
    parser = ArgumentParser()
    
    parser.add_argument( "-i", "--member_id", type=int, default=99473492, help="Retrieve information for a specific ID")
    parser.add_argument( "-g", "--mug", help="Get Info for MUG")
    parser.add_argument( "-m", "--members", help="Get Info for MUG")
    parser.add_argument( "-f", "--format", choices=[ "short", "full" ], default="short", help="Get Info for MUG")
    # Process arguments
    args = parser.parse_args()
    
    if args.member_id :
        member = m.get_member_by_id(args.member_id)
        pprint.pprint( member )
        
    if args.mug :
        mug = m.get_group( args.mug )
        pprint.pprint( mug )
        
    if args.members :
        members = m.get_members( args.members )
        count = 0
        for i in members:
            count = count + 1 
            if args.format == "short" :
                pprint.pprint( u"%s, %s, %s" % ( i[ "name" ], i["id" ], i[ "country"] ))
            else:
                pprint.pprint( i )
                
        print( "Total : %i" % count )
        
    