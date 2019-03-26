"""
Created on 22 Jun 2016

@author: jdrumgoole
"""

import pymongo


class MUGAlyserMongoDB(object):
    
    def __init__(self, uri="mongodb://localhost:27017/MUGS", database_name="MUGS"):

        self._uri             = uri

        if self._uri.startswith("mongodb://") or self._uri.startswith("mongodb+srv://"):
            self._client = pymongo.MongoClient(host=self._uri)
        else:
            raise ValueError("Invalid URL: %s" % self._uri)

        self._database = self._client[database_name]
        self._members = self._database["members"]
        self._groups = self._database["groups"]
        self._pastEvents = self._database["past_events"]
        self._upcomingEvents = self._database["upcoming_events"]
        self._audit = self._database["audit"]
        self._attendees = self._database["attendees"]

        self._audit.create_index([("name", pymongo.ASCENDING)])

        self._members.create_index([("location", pymongo.GEOSPHERE)])
        self._members.create_index([("name", pymongo.ASCENDING)])
        self._members.create_index([("id", pymongo.ASCENDING)])
        self._members.create_index([("batchID", pymongo.ASCENDING)])

        self._groups.create_index([("batchID", pymongo.ASCENDING)])
        self._pastEvents.create_index([("batchID", pymongo.ASCENDING)])
        self._upcomingEvents.create_index([("batchID", pymongo.ASCENDING)])
        self._attendees.create_index([("batchID", pymongo.ASCENDING)])

    @staticmethod
    def create_index(collection, field, direction, **kwargs  ):
        collection.create_index([( field, direction )], **kwargs )

    def drop(self, database_name):
        self._client.drop_database(database_name)

    def client(self):
        return self._client
    
    def database(self) :
        return self._database
    
    def make_collection(self, collection_name):
        return self._database[collection_name]
    
    def collection_stats(self, collection_name):
        return self._database.command("collstats", collection_name )
    
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
