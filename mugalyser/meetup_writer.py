'''
Created on 21 Nov 2016

@author: jdrumgoole
'''

from mugalyser.batchwriter import BatchWriter
from requests import HTTPError
import logging
from mugalyser.apikey import get_meetup_key
from mugalyser.meetup_api import MeetupAPI


def mergeEvents( writer ):
    for attendee, event in writer:
        doc = { u"attendee" : attendee,
                u"event" : event }
        yield doc 
        
class MeetupWriter(object):
    '''
    A class that reads data about MUGS from the Meetup API using the MeetupAPI class and writes that
    data to a MongoDB collection. Currently supports the pro API.
    '''
    def __init__(self, audit, urls, apikey= get_meetup_key(), unordered=True ):
        '''
        Write contents of meetup API to MongoDB
        '''

        self._mdb = audit.mdb()
        self._meetup_api = MeetupAPI( apikey )
        self._audit = audit
        self._groups = self._mdb.groupsCollection()
        self._members = self._mdb.membersCollection()
        self._attendees = self._mdb.attendeesCollection()
        self._pastEvents = self._mdb.pastEventsCollection()
        self._upcomingEvents = self._mdb.upcomingEventsCollection()
        self._mugs = []
        self._unordered = unordered
        self._urls = urls
        
        
    def process(self, collection, retrievalGenerator, processFunc, newFieldName ):
        '''
        Call batchWriter with a collection. Use retrievalGenerator to get a single
        document (this should be a generator function). Use processFunc to tranform the 
        document into a new doc (it should take a doc and return a doc).
        Write the new doc using the newFieldName.
        
        Write is done using a generator as well. The write receiver accumulates writes until a threshold
        is reached and then writes them as a batch.
        
        '''
        bw = BatchWriter( collection, processFunc, newFieldName, orderedWrites=self._unordered )
        writer = bw.bulkWrite()
        
        for i in retrievalGenerator :
            writer.send( i )

    
    def processAttendees( self, group ):
        
        writer = self._meetup_api.get_attendees( group, items=100)
        
        newWriter = mergeEvents( writer )
        self.process( self._attendees, newWriter, self._audit.addTimestamp, "info"  )
        
    def processGroup(self, url_name, groupName="group"):
        group = self._meetup_api.get_group( url_name )
        newDoc = self._audit.addTimestamp( groupName, group )
        self._groups.insert_one( newDoc )
        return newDoc

    def updateGroup(self, groupName, doc ):
        self._mugs.append( doc[ "urlname" ])
        return self._audit.addTimestamp( groupName, doc )
        
    def processGroups(self, nopro ):
        if nopro:
            groups = self.get_groups()
        else:
            groups = self._meetup_api.get_pro_groups()
            
        self.process( self._groups,  groups, self.updateGroup, "group" )
        
    def get_groups(self ):
        for i in self._urls:
            yield self._meetup_api.get_group( i )
        
    def processPastEvents(self, url_name ):
        pastEvents = self._meetup_api.get_past_events( url_name )
        self.process( self._pastEvents, pastEvents, self._audit.addTimestamp, "event" )
   
    def processUpcomingEvents(self, url_name ):
        upcomingEvents = self._meetup_api.get_upcoming_events( url_name )
        self.process( self._upcomingEvents, upcomingEvents, self._audit.addTimestamp, "event" )
        
    def processMembers( self, nopro ):
        
        if nopro:
            members = self.get_members()
        else:
            members = self._meetup_api.get_pro_members()
        self.process( self._members, members, self._audit.addTimestamp, "member" )
        
    def get_members(self ):
        for i in self._urls:
            yield self._meetup_api.get_members( i )
            
        
    def capture_complete_snapshot(self, nopro=True ):
        
        logging.info( "Capturing complete snapshot" )

        if nopro:
            logging.info( "processing groups (nopro)")
            self.processNoProGroups()
        else:
            logging.info( "processing groups (pro)")
            self.processGroups()

        if nopro:
            logging.info( "processing members (nopro)")
            self.processNoProMembers()
        else:
            logging.info( "processing members (pro)")
            self.processMembers()
        for url_name in self._mugs :
            logging.info( "process past events for      : %s", url_name )
            self.processPastEvents( url_name )
            logging.info( "process upcoming events for  : %s", url_name )
            self.processUpcomingEvents( url_name )
            logging.info( "process attendees for        : %s", url_name )
            self.processAttendees( url_name )
            
    def mug_list(self):
        return self._mugs
    
    
    def capture_snapshot(self, url_name, nopro, admin_arg, phases ):

        try :
        
            for i in phases:
                if i == "pastevents" :
                    logging.info( "process past events for      : %s", url_name )
                    self.processPastEvents( url_name )
                elif i == "upcomingevents" :
                    logging.info( "process upcoming events for  : %s", url_name )
                    self.processUpcomingEvents( url_name )
                elif i == "attendees" :
                    if admin_arg:
                        logging.info( "process attendees       : '%s'", url_name )
                        self.processAttendees( url_name )
                    else:
                        logging.warn( "You have not specified the admin arg")
                        logging.warn( "You must be a meetup admin user to request attendees")
                        logging.warn( "Ignoring phase 'attendees")
            
                else:
                    logging.warn( "ignoring phase '%s': not a valid execution phase", i )
    
        except HTTPError, e :
            logging.fatal( "Stopped processing: %s", e )
            raise

  
    def capture_snapshot_by_phases(self, url_name, nopro, admin_arg, phases ):
            
        try :
        
            for i in phases:
                if  i == "groups" :
                    self.processGroup( url_name )
                
                elif i == "pastevents" :
                    logging.info( "Getting past events     : '%s'", url_name )
                    self.processPastEvents( url_name )
                
                elif i == "upcomingevents" :
                    logging.info( "Getting upcoming events : '%s'", url_name )
                    self.processUpcomingEvents( url_name )
                
                elif  i == "members" :
                    logging.info( "Getting members         : '%s'", url_name )
                    self.processMembers()
                    
                elif i == "attendees" :
                    if admin_arg:
                        logging.info( "Getting attendees       : '%s'", url_name )
                        self.processAttendees( url_name )
                    else:
                        logging.warn( "You have not specified the admin arg")
                        logging.warn( "You must be a meetup admin user to request attendees")
                        logging.warn( "Ignoring phase 'attendees")
                else:
                    logging.warn( "%s is not a valid execution phase", i )
    
        except HTTPError, e :
            logging.fatal( "Stopped processing: %s", e )
            raise




