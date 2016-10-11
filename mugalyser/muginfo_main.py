'''
Created on 10 Oct 2016

Simple program to Dump group data..

@author: jdrumgoole
'''
from argparse import ArgumentParser
import sys

from mugs import MUGS
from mongodb import MUGAlyserMongoDB
from audit import AuditDB

def getCountryMugs( mugs, country ):
    for k,v in mugs.iteritems() :
        if v[ "country"] == country :
            yield (v[ "country"], k )
            
if __name__ == '__main__':
            
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017", help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "-g", "--hasgroup", nargs="+", default=[], help="Is this a MongoDB Group")
    
    parser.add_argument( "-l", "--listgroups", action="store_true", default=False,  help="print out all the groups")
    
    parser.add_argument( "-c", "--listcountry", nargs="+", default=[],  help="print groups by country")
    
    parser.add_argument( "-b", "--batches", action="store_true", default=False, help="List all the batches in the audit database [default: %(default)s]")
    
    args = parser.parse_args()
    
    if args.host:
        mdb = MUGAlyserMongoDB( host=args.host )
        
    for i in args.hasgroup:
        if i in MUGS:
            print( "{:40} :is a MongoDB MUG".format( i ))
        else:
            print( "{:40} :is not a MongoDB MUG".format( i ))
        
    if args.listgroups:
        for mug,location in MUGS.iteritems():
            print( "{:40} (location: {})".format( mug, location["country"] ))
        print( "%i total" % len( MUGS ))
        
    count = 0
    for i in args.listcountry:
        byCountry = getCountryMugs( MUGS, i )
        for mug, location  in byCountry :
            count = count +1
            print( "{:20} has MUG: {}".format( mug, location ))
        print( "%i total" % count )
        
    if args.batches :
        if not args.host:
            print( "Need to specify --host for batchIDs")
            sys.exit( 2 )
        audit = AuditDB( mdb )
        batchIDs = audit.getBatchIDs()
        for b in batchIDs :
            print( b )
        
            
    