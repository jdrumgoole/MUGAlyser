'''
Created on 28 Dec 2016

@author: jdrumgoole
'''
from argparse import ArgumentParser
from mugalyser.agg import Agg
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from mugalyser.groups import EU_COUNTRIES, Groups
import pprint
import pymongo
import json
from datetime import datetime

def printCursor( c, filterField=None, filterList=None ):
    count = 0 
    for i in c :
        if filterField and filterList :
            if i[ filterField ]  in filterList:
                pprint.pprint( i )
        else:
            print( json.dumps( i ))
        count = count + 1
    print( "Total records: %i" % count )

        
def getMembers( mdb, batchID ):
     
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

def meetupTotals( mdb, batchID, region=None ):
    
    agg = Agg( mdb.pastEventsCollection())
    
    groups = Groups( mdb )
    urls = groups.get_region_group_urlnames( region )
    
    agg.addMatch({ "batchID"      : batchID,
                   "event.status" : "past",
                   "event.group.urlname" : { "$in" : urls }} )
    
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
    return agg.aggregate()
    
def get_events(mdb, batchID, startDate=None, endDate=None, rsvpbound=0):
    agg = batchMatch(mdb.pastEventsCollection(), batchID )
    
    if startDate is not None : #and type( startDate ) == datetime :
        agg.addMatch( { "event.time" : { "$gte" : startDate }})
        
    if endDate is not None:
        agg.addMatch( { "event.time" : { "$lte" : endDate }})
        
    if rsvpbound > 0 :
        agg.addMatch( { "event.yes_rsvp_count" : { "$gte" : rsvpbound }})
        pass
    
    agg.addProject( { "_id": 0, 
                      "group"        : "$event.group.urlname", 
                      "rsvp_count"   : "$event.yes_rsvp_count",
                      "time"         : "$event.time" })
        
    agg.addSort( { "time" : 1 })
    return agg.aggregate()
    
def get_country_events( mdb, batchID, country, startDate=None, endDate=None, rsvpbound=0 ):
    
    cursor = get_events( mdb, batchID, startDate, endDate, rsvpbound=rsvpbound )
    
    groups = Groups( mdb )
    urls = groups.get_country_group_urlnames( country )
    
    printCursor( cursor, "group", urls )
    
def get_region_events( mdb, batchID, countries, startDate=None, endDate=None, rsvpbound=0):
    
    cursor = get_events( mdb, batchID, startDate, endDate, rsvpbound=rsvpbound )
    
    groups = Groups( mdb )
    urls = groups.get_region_group_urlnames( countries )

    printCursor( cursor, "group", urls )
    
if __name__ == '__main__':
    
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    args = parser.parse_args()
    
    mdb = MUGAlyserMongoDB( uri=args.host )
    
    audit = Audit( mdb )
    
    batchID = audit.getCurrentValidBatchID()

    print( "USA Meetup Totals")
    meetupTotals( mdb, batchID, region = [ 'USA'] )
    
    print( "" )
    
    print( "EU Meetup Totals")
    meetupTotals( mdb, batchID, region = EU_COUNTRIES )
    
    print( "" )
    
    groupTotals(mdb, batchID )
    
    print( "" )
    
    getMembers( mdb, batchID )
    
    print( "" )
    
    get_eu_mugs(mdb, batchID)
    
    print( "" )
    
    get_region_events(mdb, batchID, EU_COUNTRIES, startDate=datetime( 2016, 1, 1 ), rsvpbound=10)
    
    print( " ")

    events = get_country_events( mdb, batchID, "USA", startDate=datetime( 2016, 1, 1 ), rsvpbound=10 )
    
    print( " " )
        
        