#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 17 Nov 2016

@author: jdrumgoole
'''

import sys
<<<<<<< HEAD
=======
import pprint
>>>>>>> parent of 8fc37f7... WIP

import pprint
from argparse import ArgumentParser
from meetup_api import MeetupAPI
from events import Events
<<<<<<< HEAD
from members import Members
from groups import Groups
from traceback import print_exception

from mugalyser.generator_utils import printCount
    
program_name = "meetup_info_main"

def main( argv = None ) :
=======
from groups import Groups


from mugalyser.generator_utils import printCount
    

def main() :
    parser = ArgumentParser()
    
    parser.add_argument( "--apikey", default="", help="API Key to use for Calls")
    parser.add_argument( "-i", "--member_id", type=int, help="Retrieve information for a specific ID")
    parser.add_argument( "-g", "--mug", help="Get Info for MUG")
    parser.add_argument( "--members", nargs="+", default=[],  help="list all members of a list of groups")
    parser.add_argument( "-l", "--listgroups", action="store_true", default=False, help = "List all groups")
    parser.add_argument( "-u", "--urlnames", action="store_true", default=False, help = "List all groups by URL name")
    parser.add_argument( "--pastevents", nargs="+", default=[], help="Get past events for MUG")
    parser.add_argument( "--upcomingevents", nargs="+", default=[], help="Get upcoming events for MUG")
    parser.add_argument( "-f", "--format_type", choices=[ "oneline", "summary", "full" ], default="short", help="type of output ")
    # Process arguments
    args = parser.parse_args()
>>>>>>> parent of 8fc37f7... WIP
    
    if argv:
        sys.argv.extend( argv )
        
    try :
        parser = ArgumentParser()
        
        parser.add_argument( "--apikey", default="", help="API Key to use for Calls")
        parser.add_argument( "-i", "--member_id", type=int, help="Retrieve information for a specific ID")
        parser.add_argument( "-g", "--mug", help="Get Info for MUG")
        parser.add_argument( "--members", nargs="+", default=[],  help="list all members of a list of groups")
        parser.add_argument( "-l", "--listgroups", action="store_true", default=False, help = "List all groups")
        parser.add_argument( "-u", "--urlnames", action="store_true", default=False, help = "List all groups by URL name")
        parser.add_argument( "--pastevents", nargs="+", default=[], help="Get past events for MUG")
        parser.add_argument( "--upcomingevents", nargs="+", default=[], help="Get upcoming events for MUG")
        parser.add_argument( "-f", "--format_type", choices=[ "oneline", "summary", "full" ], default="short", help="type of output ")
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
            
        if args.mug :
            mug = m.get_group( args.mug )
            pprint.pprint( mug )
            
        if args.members :
            print( "args.members : %s" % args.members )
            members = Members( mdb )
            
            q = Query()
            if args.start and not args.finish :
                q.add_range( "member.join_time", parse( args.start), datetime.now())
            elif not args.start and args.finish:
                q.add_range( "member.join_time", datetime.now(), parse( args.finish ))
            elif args.start and args.finish :
                q.add_range( "member.join_time", parse( args.start ), parse( args.finish )) 
                
            if "all" in args.members : 
                it = members.get_all_members( q )
            else:
                it = members.get_many_group_members( args.members, q )
                
<<<<<<< HEAD
            for i in it :
                count = count + 1
                #
                # sometimes country is not defined.
                #
                country = i[ "member" ].pop( "country", "Undefined")
    
                if "member_id" in i["member"] : # PRO API member format
                    print( u"{:30}, {:20}, {:20}".format( i["member"][ "member_name"], country, i["member"][ "member_id"]) )
                else:
                    print( u"{:30}, {:20}, {:20}".format( i["member"][ "name"], country, i["member"][ "id"]) )
                
            print( "%i total" % count )
        if args.pastevents :
            past_events = m.get_past_events( args.pastevents )
            printCount( past_events, args.format_type, Events.doc_print )
            
        if args.upcomingevents :
            upcoming_events = m.get_upcoming_events( args.upcomingevents )
            printCount( upcoming_events, args.format_type, Events.doc_print )
            
            
        if args.listgroups :
            printCount( m.get_pro_groups(), args.format_type, Groups.printGroup )
            
        #hack
        def printer( i, formatter ):
            print( i )
            
        if args.urlnames :
            printCount( m.get_group_names(), args.format_type, printer )
            
    except KeyboardInterrupt:
        print("Keyboard interrupt : Exiting...")
        sys.exit( 2 )

    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print_exception( exc_type, exc_value, exc_traceback )
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2
>>>>>>> 3166632a1b800f1f4ab1e982c733eb7acd2ebc95
=======
        print( "Total : %i" % count )
        
    if args.pastevents :
        past_events = m.get_past_events( args.pastevents )
        printCount( past_events, args.format_type, Events.doc_print )
        
    if args.upcomingevents :
        upcoming_events = m.get_upcoming_events( args.upcomingevents )
        printCount( upcoming_events, args.format_type, Events.doc_print )
        
        
    if args.listgroups :
        printCount( m.get_pro_groups(), args.format_type, Groups.printGroup )
        
    #hack
    def printer( i, formatter ):
        print( i )
        
    if args.urlnames :
        printCount( m.get_group_names(), args.format_type, printer )
        
>>>>>>> parent of 8fc37f7... WIP
        
    return 0

if __name__ == '__main__':
    sys.exit( main())

        
    