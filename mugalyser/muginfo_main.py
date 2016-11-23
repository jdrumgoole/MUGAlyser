'''
Created on 10 Oct 2016

Simple program to Dump group data..

@author: jdrumgoole
'''
from argparse import ArgumentParser
import sys
from pprint import pprint

from mongodb import MUGAlyserMongoDB
from audit import Audit
from .events import Events
from .members import Members
from .events import UpcomingEvents, PastEvents, Events
from .groups import Groups

def getCountryMugs( mugs, country ):
    for k,v in mugs.iteritems() :
        if v[ "country"] == country :
            yield (v[ "country"], k )
            
if __name__ == '__main__':
            
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017", help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--hasgroup", nargs="+", default=[], help="Is this a MongoDB Group")
    
    parser.add_argument( "--listgroups", action="store_true", default=False,  help="print out all the groups")
    
    parser.add_argument( "--groups", nargs="+", default=[], help="filter by this list of groups")
    parser.add_argument( "--members", action="store_true", default=False,  help="list all users")

    parser.add_argument( "--memberid", help="get info for member id")
    
    parser.add_argument( "--membername",  help="get info for member id")
    
    parser.add_argument( "--upcomingevents", default=False, action="store_true",  help="List upcoming events")
    
    parser.add_argument( "--pastevents", default=False, action="store_true",  help="List past events")
    
    parser.add_argument( "--country", nargs="+", default=[],  help="print groups by country")
    
    parser.add_argument( "--batches", action="store_true", default=False, help="List all the batches in the audit database [default: %(default)s]")
    
    parser.add_argument( "--curbatch", action="store_true", default=False, help="Report current batch ID")
    
    parser.add_argument( "--summary", default=False, action="store_true",  help="print a summary")
    args = parser.parse_args()
    
    if args.host:
        mdb = MUGAlyserMongoDB( uri=args.host )
        
    if args.curbatch :
        audit = Audit( mdb )
        curbatch = audit.getCurrentBatchID()
        print ( "current batch ID = {'batchID': %i}" % curbatch )
        
    if args.memberid :
        member = mdb.membersCollection().find_one( { "member.id" : args.memberid })
        if member :
            pprint( member )
        else:
            print( "No such member: %s" % args.memberid )
            
    if args.membername :
        member = mdb.membersCollection().find_one( { "member.name" : args.membername })
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
            count = count +1
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
            
    if args.members:
        
        count = 0
        collection = Members( mdb )

        if args.group : 
            members = collection.get_by_group(args.group )
        else:
            members = collection.get_members()
            
        for i in members :
            member = collection.get_by_ID( i[ "_id"] )
            count = count + 1
            #print( "member: %s" % member )
            
            country = member.pop( "country", "Undefined")

            print( u"{:30}, {:20}, {:20}".format( member[ "name"], country, member[ "id"]) )
            
        print( "%i total" % count )
        
        n = collection.bruteCount()
        print( "BruteCount :%i" % n)
        
    if args.upcomingevents:
        events = UpcomingEvents( mdb )
        
        count = 0
        rsvp = 0 
        for i in events.get_groups_events( args.groups ):
            count = count + 1
            if args.summary:
                print( events.summary( i[ "event" ]))
            else:
                pprint( i[ "event" ] )
                
            rsvp = rsvp + i["event"][ "yes_rsvp_count"]
        print( "Total RSVP count: %i" % rsvp )
        print( "Total Event count: %i" % count )
        
    