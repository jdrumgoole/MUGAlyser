#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 17 Nov 2016

@author: jdrumgoole
'''

import sys
import pprint
from argparse import ArgumentParser
from mugalyser.meetup_api import MeetupAPI
from traceback import print_exception
from mugalyser.mugdata import printCursor
    
program_name = "meetup_info_main"
    

def main( ) :
        
    try :
        parser = ArgumentParser( description = "A direct interface to the meetup API")
        
        parser.add_argument( "--apikey", default="", help="API Key to use for Calls")
        parser.add_argument( "-i", "--member_id", type=int, help="Retrieve information for a specific ID")
        parser.add_argument( "-g", "--mugs", nargs="+", help="Get Info for MUG")
        parser.add_argument( "--members", default=False, action="store_true",  help="list all members of a list of groups")
        parser.add_argument( "-l", "--listgroups", action="store_true", default=False, help = "List all groups")
        parser.add_argument( "--groups", default=False, action="store_true",  help="list group data for groups")
        parser.add_argument( "-u", "--urlnames", action="store_true", default=False, help = "List all groups by URL name")
        parser.add_argument( "--pastevents", nargs="+", default=[], help="Get past events for MUG")
        parser.add_argument( "--upcomingevents", nargs="+", default=[], help="Get upcoming events for MUG")
        parser.add_argument( "--attendees", nargs="+", default=[], help="Get attendees for list of groups")
        # Process arguments
        args = parser.parse_args()
        
        if args.apikey == "" :
            m = MeetupAPI()
        else:
            m = MeetupAPI( apikey = args.apikey )
            
        if args.member_id :
            member = m.get_member_by_id( args.member_id )
            pprint.pprint( member )
            print( member )
            
        if args.groups :
            for i in args.mugs:
                mug = m.get_group( i )
                pprint.pprint( mug )
            
        if args.members :
            print( "args.members: %s" % args.mugs )
            for i in args.mugs:
                it = m.get_members( i )

            count = 0 
            for j in it :
                #pprint.pprint( i )
                count = count + 1
                pprint.pprint( j )
                #print( u"{:30}, {:20}, {:20}, {:20}".format( j[ "member_name"], j[ "urlname" ], j[ "country" ], j[ "member_id"]) )

            print( "%i total" % count )
        
        if args.pastevents :
            past_events = m.get_past_events( args.pastevents )
            printCursor( past_events )
            
        if args.upcomingevents :
            upcoming_events = m.get_upcoming_events( args.upcomingevents )
            printCursor( upcoming_events )
            
        if args.attendees :
            attendees = m.get_all_attendees( args.attendees )
            printCursor( attendees )
            
        if args.listgroups :
            printCursor( m.get_pro_groups())
            
        if args.urlnames :
            for i in m.get_pro_group_names():
                print( i )
            
    except KeyboardInterrupt:
        print("Keyboard interrupt : Exiting...")
        sys.exit( 2 )

    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print_exception( exc_type, exc_value, exc_traceback )
        indent = len( "mug_info_main" ) * " "
        sys.stderr.write("mug_info_main" + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2
        
    return 0

if __name__ == '__main__':
    sys.exit( main())

        
    