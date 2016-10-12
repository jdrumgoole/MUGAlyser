'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

import pymongo
import logging


class MUGAlyserMongoDB( object ):
    
    def __init__(self, host="localhost", port=27017, databaseName="MUGS", replset="",
                 username=None, password=None, ssl=False, admin="admin", connect=True):
        
        self._host = host
        self._port = port
        self._databaseName = databaseName
        self._database = None
        self._collection = None
        self._username = username
        self._password = password
        self._replset = replset
        self._ssl = ssl
        self._logger = logging.getLogger( databaseName )
        self._admin = admin
        self._client = None
        self._members         = None
        self._groups          = None
        self._pastEvents      = None
        self._upcomingEvents  = None
        
        if connect:
            self.connect()
            
    def connect(self ):

        if self._host.startswith( "mongodb://" ) :
            self._client = pymongo.MongoClient( host=self._host )
        else:
            self._client = pymongo.MongoClient( host=self._host, port=self._port, ssl=self._ssl, replicaSet=self._replset )
            
        self._database = self._client[ self._databaseName]
        
        if self._username :
            #self._admindb = self._client[ self._admin ]
            if self._database.authenticate( name=self._username, password=self._password, source=self._admin ):
#            if self._database.authenticate( self._username, self._password, mechanism='MONGODB-CR'):
                logging.debug( "successful login by %s (method SCRAM-SHA-1)", self._username )
            else:
                logging.error( "login failed for %s (method SCRAM-SHA-1)", self._username )
                
        self._members         = self._database[ "members" ]
        self._groups          = self._database[ "groups" ]
        self._pastEvents      = self._database[ "past_events" ]
        self._upcomingEvents  = self._database[ "upcoming_events" ]
        
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

    def membersCollection(self):
        return self._members
    