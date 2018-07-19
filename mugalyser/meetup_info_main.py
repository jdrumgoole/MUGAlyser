#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 17 Nov 2016

@author: jdrumgoole
'''

import sys
import pprint
from argparse import ArgumentParser
import logging

from mugalyser.meetup_api import MeetupAPI
from traceback import print_exception
from mugalyser.mugdata import printCursor
from mugalyser.apikey import get_meetup_key
    
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
        parser.add_argument( "--loop", type=int, default=1, help="Loop call for --loop times")
        parser.add_argument( "--reshape", default=False, action="store_true", help="Reshape output for BSON" )
        parser.add_argument( "--req", default=False, action="store_true", help="Report underlying request URL to meetup")
        # Process arguments
        args = parser.parse_args()
        
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=format_string, level=logging.INFO )
        if args.apikey == "" :
            m = MeetupAPI( apikey= get_meetup_key(), reshape=args.reshape )
        else:
            m = MeetupAPI( apikey = args.apikey, reshape=args.reshape )
            
        for i in range( args.loop ):
            if args.member_id :
                (url, member) = m.get_member_by_id( args.member_id )
                if args.req:
                    print("req: '{}'".format(url))
                pprint.pprint( member )
                
            if args.groups :
                for i in args.mugs:
                    (url, mug)= m.get_group( i )
                    if args.req:
                        print("req: '{}'".format(url))
                    pprint.pprint( mug )
                
            if args.members :
                print( "args.members: %s" % args.mugs )
                #it = m.get_members( args.mugs )
    
                count = 0 
                name=""
                mid=""
                for (url, j) in m.get_members( args.mugs ):
                    if args.req:
                        print("req: '{}'".format(url))
                    count = count + 1

                    if "name" in j:
                        name = j[ "name"]
                        mid = j[ "id" ]
                    else:
                        name = j[ "member_name"]
                        mid = j[ "member_id"]
                    print( u"{:30}, {:20}, {:20}, {:20}".format( name, i, j[ "country" ], mid ) )
    
                print( "%i total" % count )
            
            if args.pastevents :
                ( url, past_events)  = m.get_past_events( args.pastevents )
                if args.req:
                    print("req: '{}'".format(url))
                printCursor( past_events )
                
            if args.upcomingevents :
                (url, upcoming_events)= m.get_upcoming_events( args.upcomingevents )
                if args.req:
                    print("req: '{}'".format(url))
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

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print_exception( exc_type, exc_value, exc_traceback )
        indent = len( "mug_info_main" ) * " "
        sys.stderr.write("mug_info_main" + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2
        
    return 0

if __name__ == '__main__':
    sys.exit( main())

        
    