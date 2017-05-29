'''
Created on 21 Nov 2016

@author: jdrumgoole
'''

from mongodb_utils.batchwriter import BatchWriter
from requests import HTTPError
import logging
#import pprint
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
    data to a MongoDB collection. Supports pro and no pro APIs
    '''
    def __init__(self, audit, mdb, urls, apikey= get_meetup_key(), unordered=True ):
        '''
        Write contents of meetup API to MongoDB
        '''

        self._mdb = mdb
        self._meetup_api = MeetupAPI( apikey )
        self._audit = audit
        self._groups = self._mdb.groupsCollection()
        self._pro_groups = self._mdb.proGroupsCollection()
        self._members = self._mdb.membersCollection()
        self._pro_members = self._mdb.proMembersCollection()
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
        is reached and then writes them as a batch using BatchWriter.
        
        '''
        bw = BatchWriter( collection, processFunc, newFieldName, orderedWrites=self._unordered )
        writer = bw.bulkWrite( writeLimit=1)
        
        for i in retrievalGenerator :
            writer.send( i )

    
    def processAttendees( self, group ):
        
        writer = self._meetup_api.get_attendees( group )
        
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
        
        
    def process_nopro_groups(self ):
        groups = self.get_groups()
        self.process( self._groups,  groups, self.updateGroup, "group" )
        
    def process_pro_groups(self):
        groups = self._meetup_api.get_pro_groups()
        self.process( self._pro_groups,  groups, self.updateGroup, "group" )
        
    def processGroups(self, collect ):
        if collect == "nopro":
            self.process_nopro_groups()
        elif collect == "pro":
            self.process_pro_groups()
        else:
            self.process_pro_groups()
            self.process_nopro_groups()

    def get_groups(self ):
        for i in self._urls:
            yield self._meetup_api.get_group( i )
        
    def processPastEvents(self, url_name ):
        pastEvents = self._meetup_api.get_past_events( url_name )
        self.process( self._pastEvents, pastEvents, self._audit.addTimestamp, "event" )
   
    def processUpcomingEvents(self, url_name ):
        upcomingEvents = self._meetup_api.get_upcoming_events( url_name )
        self.process( self._upcomingEvents, upcomingEvents, self._audit.addTimestamp, "event" )
        
    def process_pro_members(self):
        members = self._meetup_api.get_pro_members()
        self.process( self._pro_members, members, self._audit.addTimestamp, "member" )
    
    def process_nopro_members(self):
        members = self.get_members()
        self.process( self._members, members, self._audit.addTimestamp, "member" )
        
    def processMembers( self, collect ):
        if collect == "nopro":
            self.process_nopro_members()
        elif collect == "pro":
            self.process_pro_members()
        else:
            self.process_pro_members()
            self.process_nopro_members() 
        
    def get_members(self ):
        for i in self._urls:
            for member in self._meetup_api.get_members( i ):
#                 if member.has_key( "name" ) :
#                     print( member[ "name"] )
#                 else:
#                     pprint.pprint( member )
                yield member
            
    def mug_list(self):
        return self._mugs
    
    
    def capture_snapshot(self, url_name,  admin_arg, phases ):

        try :
        
            for i in phases:
                if i == "pastevents" :
                    logging.info( "process past events for      : '%s'", url_name )
                    self.processPastEvents( url_name )
                elif i == "upcomingevents" :
                    logging.info( "process upcoming events for  : '%s'", url_name )
                    self.processUpcomingEvents( url_name )
                elif i == "attendees" :
                    if admin_arg:
                        logging.info( "process attendees            : '%s'", url_name )
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





