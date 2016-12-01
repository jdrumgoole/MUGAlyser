'''
Created on 10 Oct 2016

Simple program to Dump group data..

@author: jdrumgoole
'''
from argparse import ArgumentParser
import sys
from pprint import pprint

from audit import Audit
from mongodb import MUGAlyserMongoDB
from members import Members, Organizers
from events import UpcomingEvents, PastEvents, Events
from groups import Groups
from utils import printCount

def report_events( e, groups ):
        
    count = 0
    rsvp = 0 
    printCount( e.get_groups_events( groups ))
    for i in e.get_groups_events( groups, pprint, ):
        count = count + 1
        if args.summary:
            print( e.summary( i[ "event" ]))
        else:
            pprint( i[ "event" ] )
            
        rsvp = rsvp + i["event"][ "yes_rsvp_count"]
    print( "Total RSVP count: %i" % rsvp )
    print( "Total Event count: %i" % count )
    
def getCountryMugs( mugs, countrycode ):
    for k,v in mugs.iteritems() :
        if v[ "country"] == countrycode :
            yield (v[ "country"], k )
            
            
if __name__ == '__main__':
            
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017", help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--hasgroup", nargs="+", default=[], help="Is this a MongoDB Group")
    
    parser.add_argument( "-l", "--listgroups", action="store_true", default=False,  help="print out all the groups")
    
    parser.add_argument( "--members", nargs="+", default=[],  help="list all members of a list of groups")
    
    parser.add_argument( "--distinct" , action="store_true", default=False, help="List all distinct members")

    parser.add_argument( "-i", "--memberid", help="get info for member id")
    
    parser.add_argument( "--membername",  help="get info for member id")
    
    parser.add_argument( "--upcomingevents", nargs="+", default=[],  help="List upcoming events")
    
    parser.add_argument( "--pastevents",  nargs="+", default=[],  help="List past events")
    
    parser.add_argument( "--country", nargs="+", default=[],  help="print groups by country")
    
    parser.add_argument( "--batches", action="store_true", default=False, help="List all the batches in the audit database [default: %(default)s]")
    
    parser.add_argument( "--curbatch", action="store_true", default=False, help="Report current batch ID")
    
    parser.add_argument( "--organizer", nargs="+", default=[], help="List organizers for a specific set of MUGS" )
    
    parser.add_argument( "-f", "--format_type", choices=[ "oneline", "summary", "full" ], default="oneline", help="type of output")
    # Process arguments
    args = parser.parse_args()
    
    if args.host:
        mdb = MUGAlyserMongoDB( uri=args.host )
        
        
    members = Members( mdb )
    
    if args.curbatch :
        audit = Audit( mdb )
        curbatch = audit.getCurrentBatchID()
        print ( "current batch ID = {'batchID': %i}" % curbatch )
        
    if args.memberid :
        member = members.find_one( { "member.id" : args.memberid })
        if member :
            pprint( member )
        else:
            print( "No such member: %s" % args.memberid )
            
    if args.membername :
        member = members.find_one( { "member.name" : args.membername })
        if member :
            pprint( member )
        else:
            print( "No such member: %s" % args.membername )
              
    for i in args.hasgroup:

        groups = Groups( mdb )
        if groups.get_group( i ) :
            print( "{:40} :is a MongoDB MUG".format( i ))
        else:
            print( "{:40} :is not a MongoDB MUG".format( i ))
        
    if args.listgroups:
        groups = Groups( mdb )
        count = 0 
        for g in groups.get_all_groups() :
            count = count + 1 
            print( "{:40} (location: {})".format( g[ "group"][ "urlname" ], g["group"]["country"] ))
        print( "total: %i" % count )
        
    if args.country: 
        count = 0
        groups = Groups( mdb )
        country_groups = groups.find( { "group.country" : args.country })
        for g in country_groups :
            count = count + 1
            print( "{:20} has MUG: {}".format( g[ "group"]["urlname"], args.country ))
            print( "total : %i " % count )
        
    if args.batches :
        if not args.host:
            print( "Need to specify --host for batchIDs")
            sys.exit( 2 )
        audit = Audit( mdb )
        batchIDs = audit.getBatchIDs()
        for b in batchIDs :
            print( b )
            
    count = 0
    if args.members:
        print( "args.members : %s" % args.members )
        members = Members( mdb )
        if "all" in args.members : 
            iter = members.get_all_members()
        else:
            iter = members.get_many_group_members( args.members )
            
        for i in iter :
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

    if args.distinct:
        members = Members( mdb )
        distinct = members.distinct_members()
        printCount( distinct  )
        
    if args.upcomingevents:
        events = UpcomingEvents( mdb )
        if "all" in args.upcomingevents :
            events.count_print( events.get_all_group_events(), args.format_type )
        else:
            events.count_print( events.get_groups_events( args.upcomingevents ), args.format_type )

    if args.pastevents:
        events = PastEvents( mdb )
        events.count_print( events.get_groups_events( args.pastevents ), args.format_type )
        
    if "all" in args.organizer  :
        organizers = Organizers( mdb )
        members = organizers.get_organizers()
        organizers.count_print( members, args.format_type )
    else:
        organizers = Organizers( mdb )
        for i in args.organizer :
            print( "Organizer: '%s'" % i )
            mugs = organizers.get_mugs( i )
            for m in mugs:
                print( "\t%s" % m[ "urlname" ])
        
        
        