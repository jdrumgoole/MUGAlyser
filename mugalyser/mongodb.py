'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

import pymongo
import logging

from version import __programName__


class MUGAlyserMongoDB( object ):
    
    def __init__(self, url="mongodb://localhost:27017", databaseName="MUGS", connect=True):
        
        self._url = url
        self._logger = logging.getLogger( __programName__ )

        self._client          = None
        self._databaseName    = databaseName 
        
        self._members         = None
        self._groups          = None
        self._pastEvents      = None
        self._upcomingEvents  = None
        self._attendees       = None
        
        
        if connect:
            self.connect()
            
    def connect(self ):

        self._client = pymongo.MongoClient( host=self._url )
            
        self._database = self._client[ self._databaseName]
                
        self._members         = self._database[ "members" ]
        self._groups          = self._database[ "groups" ]
        self._pastEvents      = self._database[ "past_events" ]
        self._upcomingEvents  = self._database[ "upcoming_events" ]
        self._audit           = self._database[ "audit" ]
        self._attendees       = self._database[ "attendees"]
        
        self._members.create_index([("location", pymongo.GEOSPHERE)])
        self._members.create_index([("member.name", pymongo.ASCENDING )])
        
        self._members.create_index([( "batchID", pymongo.ASCENDING )])
        self._groups.create_index([( "batchID", pymongo.ASCENDING )])
        self._pastEvents.create_index([( "batchID", pymongo.ASCENDING )])
        self._upcomingEvents.create_index([( "batchID", pymongo.ASCENDING )])

    def database(self) :
        return self._database
    
    def pastEventsCollection(self):
        return self._pastEvents
    
    def upcomingEventsCollection(self):
        return self._upcomingEvents
    
    def groupsCollection(self):
        return self._groups

    def auditCollection(self):
        return self._audit
    
    def membersCollection(self):
        return self._members
    
    def attendeesCollection(self):
        return self._attendees
    