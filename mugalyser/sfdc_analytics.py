'''
Created on 7 Jul 2017

@author: jdrumgoole
'''
from dateutil.relativedelta import relativedelta
from datetime import datetime
 
from mongodb_utils.agg import Agg, CursorFormatter

class Filename( object ):
    '''
    Make a filename but accept an "-" as the name parameter. If the name
    is "-" then ignore all other parameters and write to stdout. So return
    just "-" as the filename.
    '''
    def __init__(self, prefix="", name="-", suffix="", ext=""):
        
        self._prefix = prefix
        self._name   = name
        self._suffix = suffix
        self._ext    = ext 
        
        self._filename = Filename.make( self._prefix, self._name, self._suffix, self._ext )
    
    def __str__(self):
        return self._filename
    
    def __repr__(self):
        return self._filename

    def suffix(self, s ):
        self._filename =Filename.make( self._prefix, self._name, s, self._ext )
        return self._filename
        
    def prefix(self, p ):
        self._filename =Filename.make( p, self._name, self._suffix, self._ext )
        return self._filename
        
    def name(self, n ):
        self._filename =Filename.make( self._prefix, n, self._suffix, self._ext )
        return self._filename
    
    @staticmethod
    def make( prefix, name, suffix, ext ):
        '''
        If root is '-" then we just return that. Otherwise
        we construct a filename of the form:
        <root><suffix>.<ext>
        '''
        if not ext.startswith( '.' ):
            ext = '.' + ext
            
        if name == "-"  or name is None:
            return "-"
        else: 
            #print( self._prefix + self._name + self._suffix + "." + self._ext )
            return prefix + name + suffix + ext

class SFDC_Analytics( object ):
            
    def __init__(self, collection, formatter="json",limit=None, view=None ):
        self._collection = collection

        self._sorter = None
        self._start_date = None
        self._end_date = None
        self._format = formatter
        self._files = []
        self._limit = limit

        self._view = view
    
    def files(self):
        return self._files
    
    
    def setRange(self, start_date, end_date ):
        self._start_date = start_date
        self._end_date = end_date      
        
    def setSort(self, sorter ):
        self._sorter = sorter
        

    def get_job_groups( self, filename=None ):
        '''
        Find all the jobs in SFCD
        '''
    
        agg = Agg( self._collection )

        # [ { "$group" : { "_id" : "$Job Function", "count" : { "$sum" : 1  }}} ]
        agg.addGroup( { "_id"   : "$Job Function",
                        "count" : { "$sum" : 1 }})
        
        if self._sorter:
            agg.addSort( self._sorter )

        print( agg )
        for i in agg() :
            print( i ) 
        formatter = CursorFormatter( agg, filename, self._format )
        formatter.output( fieldNames= [ "_id", "count" ], limit=self._limit )
        
        if filename != "-":
            self._files.append( filename )
        
    def get_events(self, urls, when="past", filename=None):
        '''
        Get events when=past means past events. when="upcoming" means future events.
        '''
    
        agg = None
        
        if when == "past" : 
            agg = Agg( self._mdb.pastEventsCollection())

        elif when == "upcoming" :
            agg = Agg( self._mdb.upcomingEventsCollection())

        
        agg.addMatch({ "batchID"      : self._batchID,
                       "event.status" : when,
                       "event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "event.time", self._start_date, self._end_date )
            
        agg.addProject( { "_id"          : 0, 
                          "group"        : u"$event.group.urlname", 
                          "name"         : u"$event.name",
                          "country"      : "$event.venue.country",
                          "rsvp_count"   : "$event.yes_rsvp_count",
                          "date"         : "$event.time" }) 
    
     
        if self._sorter:
            agg.addSort( self._sorter)

        if self._view :
            agg.create_view( self._mdb.database(), "events_view" )
            
        formatter = CursorFormatter( agg, filename, self._format )
        formatter.output( fieldNames= [ "group", "name", "rsvp_count", "date" ], datemap=[ "date"], limit=self._limit)

        if filename != "-":
            self._files.append( filename )
            
    def get_total_events( self, urls, when="past", filename=None ) :
    
        agg = None
        
        if when == "past" : 
            agg = Agg( self._mdb.pastEventsCollection())

        elif when == "upcoming" :
            agg = Agg( self._mdb.upcomingEventsCollection())

        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "event.time", self._start_date, self._end_date )
            
        agg.addMatch({ "batchID"             : self._batchID,
                       "event.status"        : when,
                       "event.group.urlname" : { "$in" : urls }} )
        
        agg.addProject( { "_id"       : 0,
                          "group"     : "$event.group.urlname",
                          "rsvp"      : "$event.group.yes_rsvp_count",
                          "month"     : { "$month" : "$event.time" },
                          "year"      : { "$year"  : "$event.time" }})
        
        agg.addGroup( { "_id" : { "month" : "$month",
                                  "year"  : "$year" },
                        "count" : { "$sum": 1 }})
        
        agg.addProject( { "month" : "$_id.month",
                          "year"  : "$_id.year",
                          "count" : "$count"} )
        
        
        if self._sorter:
            agg.addSort( self._sorter)
            
        if self._view :
            agg.create_view( self._mdb.database(), "total_events" )
            
        if filename :
            self._filename = filename
            
        formatter = CursorFormatter( agg, self._filename, self._format )
        filename = formatter.output( fieldNames= [ "month", "year", "count" ], limit=self._limit)
        
        if filename != "-":
            self._files.append( filename )
            
    def get_new_members( self, urls, filename=None ):
        '''
        Get all the members of all the groups (urls). Range is join_time.
        '''
        
        agg = Agg( self._mdb.proMembersCollection())

        agg.addMatch({ "batchID"            : self._batchID } )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "member.join_time", self._start_date, self._end_date )
            
        agg.addUnwind( "$member.chapters" )
        agg.addMatch({ "member.chapters.urlname" : { "$in" : urls }} )
            
        agg.addProject( { "_id" : 0,
                          "group"     : "$member.chapters.urlname",
                          "name"      : "$member.member_name",
                          "join_date" : "$member.join_time" } )
        
        if self._sorter:
            agg.addSort( self._sorter)

        if self._view :
            agg.create_view( self._mdb.database(), "new_members_view" )
            
        formatter = CursorFormatter( agg, filename, self._format )
        formatter.output( fieldNames= [ "group", "name", "join_date" ], datemap=[ 'join_date'], limit=self._limit)
        
        if filename != "-":
            self._files.append( filename )
            
    def get_organisers( self, urls, filename=None ):
        '''
        Get all the members of all the groups (urls). Range is join_time.
        '''
        
        agg = Agg( self._mdb.proGroupsCollection())


        agg.addMatch({ "batchID"       : self._batchID } )
        agg.addMatch({ "group.urlname" : { "$in" : urls }} ) 
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "group.created", self._start_date, self._end_date )
         
        agg.addUnwind( "$group.organizers" )
            
        agg.addGroup( { "_id" : "$group.organizers",
                        "groups" : { "$addToSet" : "$group.urlname"}})
        
        agg.addProject( { "_id" : 0,
                          "name" : "$_id.name",
                          "role" : "$_id.permission",
                          "groups" : "$groups"
                          ""})
        
        print( agg )
        if self._sorter:
            agg.addSort( self._sorter)

        if self._view :
            agg.create_view( self._mdb.database(), "new_members_view" )
            
        formatter = CursorFormatter( agg, filename, self._format )
        formatter.output( fieldNames= [ "name", "role", "groups" ], limit=self._limit)
        
        if filename != "-":
            self._files.append( filename )

    def get_rsvps( self, urls, filename=None):   
        '''
        Lookup RSVPs by user. So for each user collect how many events they RSVPed to.
        '''
        agg = Agg( self._mdb.attendeesCollection())
        
        agg.addMatch({ "batchID"            : self._batchID,
                       "info.event.group.urlname" : { "$in" : urls }} )
        
        if self._start_date or self._end_date :
            agg.addRangeMatch( "info.event.time", self._start_date, self._end_date )
        
        agg.addProject( { "_id"        : 0,
                          "attendee"   : "$info.attendee.member.name", 
                          "group"      : "$info.event.group.urlname",
                          "date"       : "$info.event.time",
                          "event_name" : "$info.event.name" })
        
#         agg.addGroup( { "_id" : {  "attendee": "$attendee", "group": "$group" },
#                         "event_count" : { "$sum" : 1 }})
#                         
#         agg.addProject( { "_id" : 0,
#                           "attendee" : "$_id.attendee",
#                           "group" : "$_id.group",
#                           "date"  : "$event.time",
#                           "event_count" : 1 } )
        
        if self._sorter :
            agg.addSort( self._sorter)

        if self._view :
            agg.create_view( self._mdb.database(), "rsvps_view" )
            
        formatter = CursorFormatter( agg, filename, self._format )
        formatter.output( fieldNames= [ "attendee", "group", "date", "event_name" ], datemap=[ "date" ],  limit=self._limit )

        if filename != "-":
            self._files.append( filename )
            
