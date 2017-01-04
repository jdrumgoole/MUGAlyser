'''
Created on 28 Dec 2016

@author: jdrumgoole
'''
from argparse import ArgumentParser
from mugalyser.agg import Agg
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
import pprint
import pymongo
import json
from datetime import datetime

EU_COUNTRIES = [ "Austria", 
                 "Belgium", 
                 "Bulgaria", 
                 "Croatia", 
                 "Cyprus", 
                 "Czech Republic", 
                 "Denmark", 
                 "Estonia", 
                 "Finland", 
                 "France", 
                 "Germany", 
                 "Greece", 
                 "Hungary", 
                 "Ireland", 
                 "Italy", 
                 "Latvia", 
                 "Lithuania", 
                 "Luxembourg", 
                 "Malta", 
                 "Netherlands", 
                 "Poland", 
                 "Portugal", 
                 "Romania", 
                 "Slovakia", 
                 "Slovenia", 
                 "Spain", 
                 "Sweden", 
                 "United Kingdom" ]

def printCursor( c ):
    count = 0 
    for i in c :
        pprint.pprint( i )
        count = count + 1
    print( "Total records: %i" % count )
        
def getMembers( mdb, batchID ):
    groups = mdb.groupsCollection()
     
    agg = batchMatch( mdb.groupsCollection(), batchID )
    agg.addProject(  { "_id" : 0, "urlname" : "$group.urlname", "member_count" : "$group.member_count" })
    agg.addSort( { "member_count" : pymongo.DESCENDING } )
    cursor = agg.aggregate()
    printCursor( cursor )
    
def getGroupInsight( mdb, batchID, urlname):
    
    groups = mdb.groupsCollection()
    agg = Agg( groups )
    agg.addMatch( { "batchID" : batchID, "group.urlname" : urlname })
    agg.addProject(  { "_id" : 0, "urlname" : "$group.urlname", "member_count" : "$group.member_count" })

def meetupTotals( mdb, batchID ):
    
    agg = Agg( mdb.pastEventsCollection())
    
    agg.addMatch({ "batchID" : batchID, "event.status" : "past" } )
    agg.addProject( { "_id"   : 0, 
                      "name"  : "$event.name", 
                      "time"  : "$event.time",  
                      "rsvp"  : "$event.yes_rsvp_count" } )
    
    agg.addGroup( { "_id"         : { "$year" : "$time"}, 
                    "total_rsvp"   : { "$sum" : "$rsvp"},
                    "total_events" : { "$sum" : 1 }})
    
    agg.addSort( { "_id" : pymongo.ASCENDING })
    
    cursor = agg.aggregate()
    
    for i in cursor:
        pprint.pprint( i )

def batchMatch( collection, batchID ):
    agg = Agg( collection )
    agg.addMatch({ "batchID" : batchID } )
    return agg

def matchGroup( mdb, batchID, urlname ):
    agg = Agg( mdb.pastEventsCollection())
    agg.addMatch({ "batchID"      : batchID, 
                   "event.status" : "past", 
                   "event.group.urlname" : urlname } )
    return agg

def groupTotals( mdb, batchID  ):
    
    agg = batchMatch(mdb.pastEventsCollection(), batchID )
    agg.addGroup( { "_id" : { "urlname" : "$event.group.urlname", 
                              "year"    : { "$year" : "$event.time"}},
                    "event_count" : { "$sum" : 1 }})
    agg.addSort( { "_id.year" : pymongo.ASCENDING })
    #agg.addSort( { "count" : pymongo.ASCENDING })
    #agg.addProject( { "_id" : 0, "event.time": 1, "event.name" : 1 })
    agg.addSort( { "_id.urlname" : pymongo.ASCENDING })
    agg.addSort( { "year" : pymongo.ASCENDING })
    cursor = agg.aggregate()
    
    count = 0
    for i in cursor:
        print( json.dumps( i ))
        count = count + 1
        
    print( "Total: %i"  % count )

def get_eu_mugs( mdb, batchID ):
    agg = batchMatch(mdb.groupsCollection(), batchID )
    agg.addMatch( {  "group.country" : { "$in" : EU_COUNTRIES }})
    agg.addProject( { "_id": 0, "group" : "$group.urlname", "country" : "$group.country", "member_count" : "$group.member_count" })
    cursor = agg.aggregate()
    printCursor( cursor )
    
def get_eu_events( mdb, batchID, startDate=None, endDate=None ):
    agg = batchMatch(mdb.pastEventsCollection(), batchID )
    
    if startDate is not None and type( startDate ) == datetime :
        agg.addMatch( { "group.time" : { "$ge" : startDate }})
        
    agg.addProject( { "_id": 0, "group" : "$group.urlname", "country" : "$group.country", "member_count" : "$group.member_count" })
    cursor = agg.aggregate()
    printCursor( cursor )
    
if __name__ == '__main__':
    
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    args = parser.parse_args()
    
    mdb = MUGAlyserMongoDB( uri=args.host )
    
    audit = Audit( mdb )
    
    batchID = audit.getCurrentValidBatchID()

    meetupTotals( mdb, batchID )
    
    print( "" )
    
    groupTotals(mdb, batchID )
    
    print( "" )
    
    getMembers( mdb, batchID )
    
    print( "" )
    
    get_eu_mugs(mdb, batchID)
    
    print( "" )
    
    #get_eu_events(mdb, batchID, datetime( 2016, 1, 1 ))
    
        
        
        