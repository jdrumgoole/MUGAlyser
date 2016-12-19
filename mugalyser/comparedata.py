'''
Created on 14 Oct 2016

@author: jdrumgoole
'''

import pymongo
import csv
import sys
from argparse import ArgumentParser
from mongodb import MUGAlyserMongoDB
from members import Members
from audit import Audit
import pprint
try:
    from apikey import get_meetup_key
except ImportError,e :
    print( "Failed to import apikey: have you run makeapikeyfile_main.py <APIKEY> : %s" % e )
    sys.exit( 2 )

if __name__ == '__main__': 
        
    parser = ArgumentParser()
        
    parser.add_argument( "--file", default="mongodb_members_16_nov.csv", help="Input file" )

    args = parser.parse_args()
    
    mdb = MUGAlyserMongoDB( "mongodb://localhost" )
    
    members = Members( mdb, get_meetup_key()).collection()
    audit = Audit( mdb ).collection() 
    
    count = 0
    notFoundCount = 0
    foundCount = 0
    csvmembers={}
    lastBatchID = Audit( mdb ).getLastBatchID()
    
    print( "Processing batch ID: %i" % lastBatchID )
    with open( args.file, "rb") as csvdata :
        with open( "csvfile.out", "w" ) as csvout:
            reader = csv.DictReader( csvdata, delimiter="," )
            for r in reader:
                #print( r )
                count = count + 1
                csvmembers[ r[" member_id" ]] = r 
                q = { "member.id" :  int( r[ " member_id" ] ), "batchID" : lastBatchID }
                #pprint.pprint( "query: %s" % q)
                if members.find_one( { "member.id" :  int( r[ " member_id" ] ), "batchID" : lastBatchID } ) :
                    #print( "%i. %s found" % ( count, r["member_name"] ))
                    foundCount = foundCount + 1
                    csvout.write( "found in db: '%s'\n" % r[" member_id"])
                else:
                    print( "%i. %s %s not found ********************" % (count, r[ " member_id" ], r[ "member_name"] ))
                    csvout.write( "not found in db: '%s %s'\n" % ( r[ " member_id"], r[ "member_name"]))
                    notFoundCount = notFoundCount + 1
                    
        
    countCSV = 0
    missing = []
    with open( "dbmembers", "w" ) as dbout:
        for i in members.find( {"batchID" : lastBatchID } ):
    
            countCSV = countCSV + 1
            if "member" in i:
                if i[ "member" ][ "id" ] in csvmembers :
                    dbout.write( (u"in csv : %s\n" % i["member"]["id"]).encode('utf-8'))
                else:
                    dbout.write( ( u"not in csv : %s\n" % i["member"]["id"]).encode('utf-8'))
                    missing.append( i["member"]["id"] )   
            else:
                print( "no member field" )
                    
            #print( "processed: %i" % countCSV )
         
    print( "Not found in CSV file: %i" % notFoundCount )   
    print( "found in CSV file: %i" % foundCount )
    print( "Total CSV docs: %i" % countCSV )
    print( "Total db docs : %i" % count )
    print( "Total Db missing : %i" % len( missing )) 
    
        
        