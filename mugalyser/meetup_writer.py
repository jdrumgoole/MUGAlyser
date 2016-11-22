'''
Created on 21 Nov 2016

@author: jdrumgoole
'''

from audit import Audit
from batchwriter import BatchWriter
from requests import HTTPError
from version import __programName__
import logging

def mergeEvents( writer ):
    for attendee, event in writer:
        doc = { "attendee" : attendee,
                "event" : event }
        yield doc 
        
class MeetupWriter(object):
    '''
    classdocs
    '''


    def __init__(self, mdb, meetup_api ):
        '''
        Write contents of meetup API to MongoDB
        '''
        self._logger = logging.getLogger( __programName__ )
        self._mdb = mdb
        self._meetup_api = meetup_api
        self._audit = Audit( mdb )
        self._groups = self._mdb.groupsCollection()
        self._members = self._mdb.membersCollection()
        self._attendees = self._mdb.attendeesCollection()
        self._pastEvents = self._mdb.pastEventsCollection()
        self._upcomingEvents = self._mdb.upcomingEventsCollection()
        
    def process(self, collection, retrievalGenerator, processFunc, newFieldName ):
        '''
        Call batchWriter with a collection. Use retrievalFunc to get a single
        document (this should be a generator function). Use processFunc to tranform the 
        document into a new doc (it should take a doc and return a doc).
        Write the new doc using the newFieldName.
        '''
        
        bw = BatchWriter( collection, self._audit, processFunc, newFieldName )
        writer = bw.bulkWrite()
        for i in retrievalGenerator :
            writer.send( i )
        
    def processAttendees( self, group ):
        
        writer = self._meetup_api.get_attendees( group, items=100)
        
        newWriter = mergeEvents( writer )
        self.process( self._attendees, newWriter, self._audit.addTimestamp, "info"  )
        
    def processGroup(self, url_name ):
        group = self._meetup_api.get_group( url_name )
        newDoc = self._audit.addTimestamp( "group", group )
        self._groups.insert_one( newDoc )
        
    def processGroups(self ):
        groups = self._meetup_api.get_groups()
        self._process( self._groups,  groups, self._audit.addTimeSTamp, "group" )

    def processPastEvents(self, url_name ):
        pastEvents = self._meetup_api.get_past_events( url_name )
        self.process( self._pastEvents, pastEvents, self._audit.addTimestamp, "event" )
   
    def processUpcomingEvents(self, url_name ):
        upcomingEvents = self._meetup_api.get_upcoming_events( url_name )
        self.process( self._upcomingEvents, upcomingEvents, self._audit.addTimestamp, "event" )
        
    def processMembers( self, url_name ):
        
        members = self._meetup_api.get_members( url_name )
        self.process( self._members, members, self._audit.addTimestamp, "member" )
        
        
    def capture_snapshot(self, url_name, phases ):
            
        try :
        
            for i in phases:
                if  i == "groups" :
                    self._processGroup( url_name )
                
                elif i == "pastevents" :
                    self._logger.info( "Getting past events     : '%s'"  % url_name )
                    self.processPastEvents( url_name )
                
                elif i == "upcomingevents" :
                    self._logger.info( "Getting upcoming events : '%s'"  % url_name )
                    self.processUpcomingEvents( url_name )
                
                elif  i == "members" :
                    self._logger.info( "Getting members         : '%s'"  % url_name )
                    self.processMembers( url_name )
                    
                elif i == "attendees" :
                    self._logger.info( "Getting attendees       : '%s'"  % url_name )
                    self.processAttendees( url_name )
                else:
                    self._logger.warn( "%s is not a valid execution phase", i )
    
        except HTTPError, e :
            self._logger.fatal( "Stopped processing: %s", e )
            raise




