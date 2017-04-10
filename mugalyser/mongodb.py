'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

import pymongo

class MUGAlyserMongoDB( object ):
    
    def __init__(self, uri="mongodb://localhost:27017/", database="MUGS",  setup=True):

    #def __init__(self, host="localhost", port=27017, databaseName="MUGS", replset="",
    #            username=None, password=None, ssl=False, admin="admin", connect=True):
        
        '''
        Example URL 
        
        mongodb://<username>:<password>@<host list>/database?<args>
        
        "mongodb://jdrumgoole:PASSWORD@mugalyser-shard-00-00-ffp4c.mongodb.net:27017,
        mugalyser-shard-00-01-ffp4c.mongodb.net:27017,
        mugalyser-shard-00-02-ffp4c.mongodb.net:27017/admin?ssl=true&replicaSet=MUGAlyser-shard-0&authSource=admin"
        
        '''
        
        self._uri             = uri 
        self._client          = None
        self._members         = None
        self._groups          = None
        self._pastEvents      = None
        self._upcomingEvents  = None
        self._attendees       = None
        
        
        if setup:
            self.setup()

        
    def setup(self ):

        if self._uri.startswith( "mongodb://" ) :
            self._client = pymongo.MongoClient( host=self._uri, tz_aware=True )
        else:
            raise ValueError( "Invalid URL: %s" % self._uri )
        
        self._database = self._client.get_default_database()
        
#         if self._username :
#             #self._admindb = self._client[ self._admin ]
#             if self._database.authenticate( name=self._username, password=self._password, source=self._admin ):
# #            if self._database.authenticate( self._username, self._password, mechanism='MONGODB-CR'):
#                 logging.debug( "successful login by %s (method SCRAM-SHA-1)", self._username )
#             else:
#                 logging.error( "login failed for %s (method SCRAM-SHA-1)", self._username )
                
        self._members         = self._database[ "members" ]
        self._groups          = self._database[ "groups" ]
        self._pastEvents      = self._database[ "past_events" ]
        self._upcomingEvents  = self._database[ "upcoming_events" ]
        self._audit           = self._database[ "audit" ]
        self._attendees       = self._database[ "attendees"]
        
        self._audit.create_index( [("name", pymongo.ASCENDING )] )
        
        self._members.create_index([("member.location", pymongo.GEOSPHERE)])
        self._members.create_index([("member.name", pymongo.ASCENDING )])
        self._members.create_index([("member.id", pymongo.ASCENDING )])
        self._members.create_index([( "batchID", pymongo.ASCENDING )])
        self._members.create_index([( "member.join_time", pymongo.ASCENDING )])
        self._members.create_index([( "member.last_access_time", pymongo.ASCENDING )])
                
        self._groups.create_index([( "batchID", pymongo.ASCENDING )])
        self._pastEvents.create_index([( "batchID", pymongo.ASCENDING )])
        self._upcomingEvents.create_index([( "batchID", pymongo.ASCENDING )])
        self._attendees.create_index([( "batchID", pymongo.ASCENDING )])
        
    def client(self):
        return self._client
    
    def database(self) :
        return self._database
    
    def make_collection(self, collection_name ):
        return self._database[ collection_name ]
    
    def collection_stats(self, collection_name ):
        return self._database.command( "collstats", collection_name )
    
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
    
    def collection_names(self ):
        return [ "groups" , "members", "attendees", "past_events" , "upcoming_events" ]