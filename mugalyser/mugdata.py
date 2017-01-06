'''
Created on 23 Nov 2016

@author: jdrumgoole
'''

from audit import Audit
from feedback import Feedback
import pprint

from enum import Enum

class Format( Enum ):
    oneline = 1
    summary = 2
    full = 3
    
def printCursor( c, filterField=None, filterList=None ):
    count = 0 
    for i in c :
        if filterField and filterList :
            if i[ filterField ]  in filterList:
                pprint.pprint( i )
        else:
            pprint.pprint( i )
        count = count + 1
    print( "Total records: %i" % count )
    
class MUGData( object ):
    
    def __init__( self, mdb, collection_name ):
        self._mdb = mdb
        self._audit = Audit( mdb )
        self._feedback = Feedback()
        self._collection = mdb.make_collection( collection_name )

    def collection(self):
        return self._collection
    
    @staticmethod
    def filter( cursor, selector, values ):
        for i in cursor:
            if i[ selector ] in values:
                yield i
        
    def find_one(self, query=None ):
        batch_query = { "batchID" : self._audit.getCurrentBatchID() }
        if query is not None:
            batch_query.update( query )
        
        #pprint.pprint( batch_query )
        return self._collection.find_one( batch_query )
        
    def find(self, q=None, *args, **kwargs ):
        
        query = { "batchID" : self._audit.getCurrentValidBatchID() } 
        if q :
            query.update( q )
            
        if args and kwargs :
            return self._collection.find( query, args, kwargs )
        elif args :
            return self._collection.find( query, args )
        elif kwargs:
            return self._collection.find( query, kwargs )
        else:
            return self._collection.find( query )

    
    def count(self, g ):
        count = 0
        for _ in g:
            count = count + 1
        return count
    
    def generator(self, cursor ):
        
        for i in cursor:
            yield i
            
    def summary(self, doc ):
        pass 
    
    def one_line(self, doc ):
        pass
    
    def full(self, doc ):
        pass
    
    def doc_print(self, doc, format_type = None  ):
        if format_type == "summary" :
            print( self.summary( doc ))
        elif format_type == "oneline" :
            print( self.one_line( doc ))
        else:
            pprint.pprint( doc )
            
    def count_print( self, iterator, format_type=None ):
        count = 0
        for i in iterator :
            count = count + 1
            self.doc_print( i, format_type  )
        print( "Total: %i" % count )