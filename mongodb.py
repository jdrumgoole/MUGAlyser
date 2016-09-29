'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

import pymongo
import logging

class MUGAlyserMongoDB( object ):
    
    def __init__(self, host, port, databaseName, 
                 username=None, password=None, ssl=False, admindb="admin"):
        self._host = host
        self._port = port
        self._databaseName = databaseName
        self._database = None
        self._collection = None
        self._username = username
        self._password = password
        self._ssl = ssl
        self._admindb = admindb
        self._logger = logging.getLogger( databaseName )
    
    def connect(self, source=None):
        
        admindb = self._admindb
        if source:
            admindb = source
            
        self._client = pymongo.MongoClient( host=self._host, port=self._port, ssl=self._ssl)
        self._database = self._client[ self._databaseName]
        
        if self._username :
            if self._database.authenticate( name=self._username, password=self._password, source=admindb):
#            if self._database.authenticate( self._username, self._password, mechanism='MONGODB-CR'):
                logging.debug( "successful login by %s (method SCRAM-SHA-1)", self._username )
            else:
                logging.error( "login failed for %s (method SCRAM-SHA-1)", self._username )
                
        self._audit           = self._database[ "audit" ]
        self._members         = self._database[ "members" ]
        self._groups          = self._database[ "groups" ]
        self._pastEvents      = self._database[ "past_events" ]
        self._upcomingEvents  = self._database[ "upcoming_events" ]
        
        self._members.create_index([("location", pymongo.GEOSPHERE)])
        self._members.create_index([("name", pymongo.ASCENDING )])

    def auditCollection(self):
        return self._audit
    
    def pastEventsCollection(self):
        return self._pastEvents
    
    def upcomingEventsCollection(self):
        return self._upcomingEvents
    
    def groupsCollection(self):
        return self._groups

    def membersCollection(self):
        return self._members
    
    def database(self):
        return self._database
    