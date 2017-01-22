'''
Created on 28 Dec 2016

@author: jdrumgoole
'''
from argparse import ArgumentParser
from mugalyser.agg import Agg, Sorter
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from mugalyser.groups import EU_COUNTRIES, NORDICS_COUNTRIES, Groups
import pprint
import pymongo
import csv
import sys
from datetime import datetime
from mugalyser.members import Members

def addJoinDate( mdb, cursor ):
    
    members = Members( mdb )
    for i in cursor :
        member = members.get_by_ID( i[ "info"]["attendee"]["member"][ "id"])
        i[ "join_date"] = member[ "join_time" ]
        yield i
        
    
def addCountry( mdb, cursor ):
    groups = Groups( mdb )
    for i in cursor:
        country = groups.get_country( i[ 'group'] )
        i[ "country"] = country
        yield i    

def printCursor( c, outfile, fmt, fieldnames=None  ):
    if fmt == "CSV" :
        printCSVCursor( c, outfile, fieldnames )
    else:
        printJSONCursor( c, outfile )
        
        
def printCSVCursor( c, outfile, fieldnames ):
    
    if outfile is None:
        outfile = sys.stdout
        
    writer = csv.DictWriter( outfile, fieldnames = fieldnames)
    writer.writeheader()
    for i in c:
        x={}
        for k,v in i.items():
            if type( v ) is unicode :
                x[ k ] = v
            else:
                x[ k ] = str( v ).encode( 'utf8')
            
        writer.writerow( {k:v.encode('utf8') for k,v in x.items()} ) #{k:v.encode('utf8') for k,v in D.items()}
    
def printJSONCursor( c, outfile ):
    count = 0 
    
    if outfile is None:
        outfile = sys.stdout
        
    for i in c :
        pprint.pprint(i, outfile )
        count = count + 1
    outfile.write( "Total records: %i\n" % count )

        
def getMembers( mdb, batchID, urls, outfile, fmt ):
    
    agg = Agg( mdb.groupsCollection())
    
    agg.addMatch({ "batchID"      : batchID,
                   "group.urlname" : { "$in" : urls }} )
     
    agg.addProject(  { "_id" : 0, 
                       "urlname" : "$group.urlname", 
                       "country" : "$group.country",
                       "member_count" : "$group.member_count" })
    agg.addSort( Sorter("member_count", pymongo.DESCENDING ))
    cursor = agg.aggregate()
    printCursor( cursor, outfile, fmt, fieldnames= [ "urlname", "country", "member_count"] )
    
def getGroupInsight( mdb, batchID, urlname):
    
    groups = mdb.groupsCollection()
    agg = Agg( groups )
    agg.addMatch( { "batchID" : batchID, "group.urlname" : urlname })
    agg.addProject(  { "_id" : 0, "urlname" : "$group.urlname", "member_count" : "$group.member_count" })

def get_group_names( mdb, region_arg ):
    
    groups = Groups( mdb )
    if region_arg == "EU" :
        urls = groups.get_region_group_urlnames( EU_COUNTRIES )
    elif region_arg == "US" :
        urls = groups.get_region_group_urlnames( [ "USA" ] )
    else:
        urls = groups.get_region_group_urlnames()
        
    return urls

    
def meetupTotals( mdb, batchID, urls, outfile, fmt ):
    

    agg = Agg( mdb.pastEventsCollection())    
                                                  
    
    agg.addMatch({ "batchID"      : batchID,
                   "event.status" : "past",
                   "event.group.urlname" : { "$in" : urls }} )
    
    agg.addProject( { "_id"   : 0, 
                      "name"  : "$event.name", 
                      "time"  : "$event.time",  
                      "rsvp"  : "$event.yes_rsvp_count" } )
    
    agg.addGroup( { "_id"          : { "$year" : "$time"}, 
                    "total_rsvp"   : { "$sum" : "$rsvp"},
                    "total_events" : { "$sum" : 1 }})
    
    agg.addProject( { "_id" : 0,
                      "year"         : "$_id",
                      "total_rsvp"   : 1,
                      "total_events" : 1 } )
    
    agg.addSort( Sorter( "year" ))
    
    cursor = agg.aggregate()
    
    printCursor( cursor, outfile, fmt=fmt, fieldnames=[ "year", "total_rsvp", "total_events"] )

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

def groupTotals( mdb, batchID, urls, outfile, fmt  ):
    

    agg = Agg( mdb.pastEventsCollection())

    agg.addMatch({ "batchID"             : batchID,
                   "event.status"        : "past",
                   "event.group.urlname" : { "$in" : urls }} )
    
    agg.addGroup( { "_id" : { "urlname" : "$event.group.urlname", 
                              "year"    : { "$year" : "$event.time"}},
                    "event_count" : { "$sum" : 1 },
                    "rsvp_count"  : { "$sum" : "$event.yes_rsvp_count" }})
    agg.addProject( { "_id" : 0,
                      "group"   : "$_id.urlname",
                      "year"    : "$_id.year",
                      "event_count" : 1,
                      "rsvp_count" : 1 } )

    sorter = Sorter()
    sorter.add( "year" )
    sorter.add( "group" )
    sorter.add( "event_count")
    sorter.add( "rsvp_count" )
    
    agg.addSort( sorter )

    cursor = agg.aggregate()

    printCursor( addCountry( mdb, cursor ), outfile, fmt, fieldnames=[  "year", "group", "country", "event_count", "rsvp_count" ] ) 

    
def get_events(mdb, batchID, urls, outfile, fmt, startDate=None, endDate=None, rsvpbound=0):

    agg = Agg( mdb.pastEventsCollection())
    
    agg.addMatch({ "batchID"      : batchID,
                   "event.status" : "past",
                   "event.group.urlname" : { "$in" : urls }} )
        
    if startDate is not None : #and type( startDate ) == datetime :
        agg.addMatch( { "event.time" : { "$gte" : startDate }})
        
    if endDate is not None:
        agg.addMatch( { "event.time" : { "$lte" : endDate }})
        
    if rsvpbound > 0 :
        agg.addMatch( { "event.yes_rsvp_count" : { "$gte" : rsvpbound }})
        pass
    
    agg.addProject( { "_id": 0, 
                      "group"        : u"$event.group.urlname", 
                      "name"         : u"$event.name",
                      "rsvp_count"   : "$event.yes_rsvp_count",
                      "date"         : { "$dateToString" : { "format" : "%Y-%m-%d",
                                                             "date"   :"$event.time"}}} ) 
 
    sorter = Sorter( "group")
    sorter.add( "rsvp_count")
    sorter.add( "date")
    agg.addSort(  sorter )
    cursor = agg.aggregate()
    printCursor( cursor, outfile, fmt, fieldnames=[ "group", "name", "rsvp_count", "date" ] ) #"day", "month", "year" ] )
    
def get_rsvps(mdb, batchID, region, outfile, fmt, startDate=None, endDate=None, rsvpbound=0):   

    agg = Agg( mdb.attendeesCollection())
    
    agg.addMatch({ "batchID"            : batchID,
                   "info.event.group.urlname" : { "$in" : urls }} )
    
    agg.addProject( { "_id"        : 0,
                      "attendee"   : "$info.attendee.member.name", 
                      "group"      : "$info.event.group.urlname",
                      "event_name" : "$info.event.name" })
    
    agg.addGroup( { "_id" : {  "attendee": "$attendee", "group": "$group" },
                    "event_count" : { "$sum" : 1 }})
                    
    agg.addProject( { "_id" : 0,
                      "attendee" : "$_id.attendee",
                      "group" : "$_id.group",
                      "event_count" : 1 } )
    
    agg.addSort( Sorter( "event_count"))
    cursor = agg.aggregate()
    printCursor( cursor, outfile, fmt, fieldnames=[ "attendee", "group", "event_count"])

def get_active( mdb, batchID, urls, outfile, fmt ):
    '''
    We define an active user as somebody who has rsvp'd to at least one event in the last six months.
    '''
    agg = Agg( mdb.attendeesCollection())
    
    agg.addMatch({ "batchID"            : batchID,
                   "info.event.group.urlname" : { "$in" : urls },
                   "info.attendee.rsvp.response" : "yes",
                   "info.event.time" : { "$gte" : datetime( 2016, 1, 1) }} )
    
#     agg.addProject( { "_id" : 0,
#                       "name" : "$info.attendee.member.name",
#                       "urlname" : "$info.event.group.urlname",
#                       "event_name" : "$info.event.name" })
    
    agg.addGroup( { "_id"    : "$info.attendee.member.name",
                    "count"  : { "$sum": 1 },
                    "groups" : { "$addToSet" : "$info.event.group.urlname" }} )
    
    agg.addSort( Sorter( "count" ))

    cursor = agg.aggregate()
    
    printCursor( cursor, outfile, fmt, fieldnames=[ "_id", "count", "groups"])
    
if __name__ == '__main__':
    
    cmds = [ "meetups", "groups", "members", "events", "rsvps", "active" ]
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    parser.add_argument( "--format", default="JSON", choices=[ "JSON", "CSV" ], help="format for output [default: %(default)s]" )
    parser.add_argument( "--output", default="-", help="format for output [default: %(default)s]" )
    parser.add_argument( "--stats",  nargs="+", default=[ "meetups" ], 
                         choices= cmds,
                         help="List of stats to output [default: %(default)s]" )
    parser.add_argument( "--country", nargs="+", default=[ "all"],
                         help="pick a region to report on [default: %(default)s]")
    
    parser.add_argument( "--url", nargs="+",
                         help="pick a URL for a group to report on [default: %(default)s]")
    
    args = parser.parse_args()
    
    if args.output == "-" :
        outfile = sys.stdout
    else:
        outfile = open( args.output, "wb" )
        
    mdb = MUGAlyserMongoDB( uri=args.host )
        
    groups = Groups( mdb )
    if "all" in args.country :
        urls = groups.get_region_group_urlnames()
    elif "EU" in args.country :
        urls = groups.get_region_group_urlnames( EU_COUNTRIES )
    elif "NORDICS" in args.country :
        urls = groups.get_region_group_urlnames( NORDICS_COUNTRIES )
    else:
        urls = groups.get_region_group_urlnames( args.country )
        
    
    audit = Audit( mdb )
    
    batchID = audit.getCurrentValidBatchID()

    if "meetups" in args.stats :
        meetupTotals( mdb, batchID, urls, outfile, args.format )
    
    if "groups" in args.stats :
        groupTotals(mdb, batchID, urls, outfile, args.format )
    
    if "members" in args.stats :
        getMembers( mdb, batchID, urls, outfile, args.format )

    if "events" in args.stats:
        get_events(mdb, batchID, urls, outfile, args.format)
        
    if "rsvps" in args.stats:
        get_rsvps( mdb, batchID, urls, outfile, args.format )
        
    if "active" in args.stats:
        get_active( mdb, batchID, urls, outfile, args.format )

  
        