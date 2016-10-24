'''
Created on 14 Oct 2016

@author: jdrumgoole
'''

import pymongo
import csv
from argparse import ArgumentParser
import sys

if __name__ == '__main__': 
        
    parser = ArgumentParser()
        
    parser.add_argument( "--file", default="/Users/jdrumgoole/Downloads/mongodb_members_all_14Oct.csv", help="Input file" )

    args = parser.parse_args()
    
    c = pymongo.MongoClient()
    db = c[ "MUGS"]
    members = db[ "members"]
    
    count = 0
    notFoundCount = 0
    foundCount = 0
    csvmembers={}
    with open( args.file, "rb") as csvdata :
        with open( "csvfile.out", "w" ) as csvout:
            reader = csv.DictReader( csvdata, delimiter="," )
            for r in reader:
                #print( r )
                count = count + 1
                csvmembers[ r[" member_id" ]] = r 
                if members.find_one( { "member.id" :  int( r[ " member_id" ] ), "batchID" : 67 } ) :
                    #print( "%i. %s found" % ( count, r["member_name"] ))
                    foundCount = foundCount + 1
                    csvout.write( "found in db: '%s'\n" % r[" member_id"])
                else:
                    print( "%i. %s not found ********************" % (count, r[ "member_name"] ))
                    csvout.write( "not found in db: '%s %s'\n" % ( r[ " member_id"], r[ "member_name"]))
                    notFoundCount = notFoundCount + 1
                    
        
    countCSV = 0
    missing = []
    with open( "dbmembers", "w" ) as dbout:
        for i in members.find( {"batchID" : 70 } ):
    
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
    
        
        