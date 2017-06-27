'''
Created on 21 Nov 2016

@author: jdrumgoole
'''

from mongodb_utils.batchwriter import BatchWriter
from requests import HTTPError
import logging
from datetime import datetime
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
    
    The process function is a generic reader function that takes a retrieval generator (provided by
    the MeetupAPI class and a processing function. It iterates over the docs returned by the
    retrieval generator and transforms then with "processFunc". The results are returned in an 
    embedded document with the key "newFieldname".
    
    '''
    
    
    def _addTimestamp( self, name, doc ):
    
        return { name : doc, "timestamp" : datetime.utcnow(), "batchID": self._batch_ID }
  
    
    def __init__(self, apikey, batch_ID, mdb, urls, unordered=True ):
        '''
        Write contents of meetup API to MongoDB
        '''

        self._mdb = mdb 
        self._meetup_api = MeetupAPI( apikey )
        self._batch_ID = batch_ID
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
        
        
    def write(self, collection, retrievalGenerator, processFunc, newFieldName ):
        '''
        Call batchWriter with a collection. Use retrievalGenerator to get a single
        document (this should be a generator function). Use processFunc to tranform the 
        document into a new doc (it should take a doc and return a doc).
        Write the new doc using the newFieldName.
        
        Write is done using a generator as well. The write receiver accumulates writes until a threshold
        is reached and then writes them as a batch using BatchWriter.
        
        '''
        bw = BatchWriter( collection, processFunc, newFieldName, self._unordered )
        
        writer = bw.bulkWrite( writeLimit=1)
        
        for i in retrievalGenerator :
            writer.send( i )

    
    def write_Attendees( self, group ):
        
        writer = self._meetup_api.get_attendees( group )
        
        newWriter = mergeEvents( writer )
        self.write( self._attendees, newWriter, self._addTimestamp, "info"  )
        
    def write_group(self, url_name, groupName="group"):
        group = self._meetup_api.get_group( url_name )
        newDoc = self._addTimestamp( groupName, group )
        self._groups.insert_one( newDoc )
        return newDoc

    def updateGroup(self, groupName, doc ):
        self._mugs.append( doc[ "urlname" ])
        return self._addTimestamp( groupName, doc )
        
        
    def write_nopro_groups(self, mug_list ):
        groups = self._meetup_api.get_groups_by_url( mug_list )
        self.write( self._groups,  groups, self.updateGroup, "group" )
        
    def write_pro_groups(self):
        groups = self._meetup_api.get_pro_groups()
        self.write( self._pro_groups,  groups, self.updateGroup, "group" )
        
    def write_groups(self, collect, mug_list ):
        if collect == "nopro":
            self.write_nopro_groups( mug_list )
        elif collect == "pro":
            self.write_pro_groups()
        else:
            self.write_pro_groups()
            self.write_nopro_groups( mug_list )

        
    def write_PastEvents(self, url_name ):
        pastEvents = self._meetup_api.get_past_events( url_name )
        self.write( self._pastEvents, pastEvents, self._addTimestamp, "event" )
   
    def write_UpcomingEvents(self, url_name ):
        upcomingEvents = self._meetup_api.get_upcoming_events( url_name )
        self.write( self._upcomingEvents, upcomingEvents, self._addTimestamp, "event" )
        
    def write_pro_members(self):
        members = self._meetup_api.get_pro_members()
        self.write( self._pro_members, members, self._addTimestamp, "member" )
    
    def write_nopro_members(self):
        members = self._meetup_api.get_members( self._urls )
        self.write( self._members, members, self._addTimestamp, "member" )
        
    def write_members( self, collect ):
        if collect == "nopro":
            self.write_nopro_members()
        elif collect == "pro":
            self.write_pro_members()
        else:
            self.write_pro_members()
            self.write_nopro_members() 
        
            
    def mug_list(self):
        return self._mugs
    
    
    def capture_snapshot(self, url_name,  admin_arg, phases ):

        try :

            for i in phases:
                if i == "pastevents" :
                    logging.info( "process past events for      : '%s'", url_name )
                    self.write_PastEvents( url_name )
                elif i == "upcomingevents" :
                    logging.info( "process upcoming events for  : '%s'", url_name )
                    self.write_UpcomingEvents( url_name )
                elif i == "attendees" :
                    if admin_arg:
                        logging.info( "process attendees            : '%s'", url_name )
                        self.write_Attendees( url_name )
                    else:
                        logging.warn( "You have not specified the admin arg")
                        logging.warn( "You must be a meetup admin user to request attendees")
                        logging.warn( "Ignoring phase 'attendeesx'")
            
                else:
                    logging.warn( "ignoring phase '%s': not a valid execution phase", i )
    
        except HTTPError, e :
            logging.fatal( "Stopped processing: %s", e )
            raise





