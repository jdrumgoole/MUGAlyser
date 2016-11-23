'''
Created on 23 Nov 2016

@author: jdrumgoole
'''

from audit import Audit
from feedback import Feedback

class MUGData( object ):
    
    def __init__( self, mdb, collection_name ):
        self._mdb = mdb
        self._audit = Audit( mdb )
        self._feedback = Feedback()
        self._collection = mdb.make_collection( collection_name )

    def collection(self):
        return self._collection
    
    def find_one(self, query=None ):
        batch_query = { "batchID" : self._audit.getCurrentBatchID() }
        if query is not None:
            batch_query.update( query )
        
        return self._collection.find_one( batch_query )
        
    def find(self, query = None ):
        batch_query = { "batchID" : self._audit.getCurrentBatchID() }
        if query is not None:
            batch_query.update( query )
        cursor = self._collection.find( batch_query )
        for i in cursor :
            yield i