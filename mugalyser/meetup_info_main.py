'''
Created on 17 Nov 2016

@author: jdrumgoole
'''

import sys
import pprint

from argparse import ArgumentParser
from meetup_api import MeetupAPI
from events import Events
from groups import Groups


def printCount( iterator, printFunc=pprint.pprint, format=None ):
    count = 0
    for i in iterator :
        count = count + 1
        if format is None:
            printFunc( i )
        else:
            printFunc( i, format  )
    print( "Total: %i" % count )
    
if __name__ == '__main__':
    
    parser = ArgumentParser()
    
    parser.add_argument( "--apikey", default="", help="API Key to use for Calls")
    parser.add_argument( "-i", "--member_id", type=int, help="Retrieve information for a specific ID")
    parser.add_argument( "-g", "--mug", help="Get Info for MUG")
    parser.add_argument( "-m", "--members", help="Get Info for MUG")
    parser.add_argument( "-l", "--listgroups", action="store_true", default=False, help = "List all groups")
    parser.add_argument( "-u", "--urlnames", action="store_true", default=False, help = "List all groups by URL name")
    parser.add_argument( "--pastevents", nargs="+", default=[], help="Get past events for MUG")
    parser.add_argument( "--upcomingevents", nargs="+", default=[], help="Get upcoming events for MUG")
    parser.add_argument( "-f", "--format", choices=[ "short", "summary", "full" ], default="short", help="Get Info for MUG")
    # Process arguments
    args = parser.parse_args()
    
    if args.apikey == "" :
        m = MeetupAPI()
    else:
        m = MeetupAPI( apikey = args.apikey )
        
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
        
    if args.pastevents :
        past_events = m.get_past_events( args.pastevents )
        printCount( past_events, Events.printEvent, args.format )
        
    if args.upcomingevents :
        upcoming_events = m.get_upcoming_events( args.upcomingevents )
        printCount( upcoming_events, Events.printEvent, args.format )
        
        
    if args.listgroups :
        printCount( m.get_pro_groups(), Groups.printGroup, args.format )
        
    def printer( i ):
        print( i )
        
    if args.urlnames :
        printCount( m.get_group_names(), printer )
        
        


        
    