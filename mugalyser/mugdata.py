'''
Created on 23 Nov 2016

@author: jdrumgoole
'''

from mugalyser.audit import Audit
from mugalyser.feedback import Feedback
import pprint
from utils.query import Query

from enum import Enum

class Format( Enum ):
    oneline = 1
    summary = 2
    full = 3

def printCount( iterator, printfunc=None ):
    count = 0
    for i in iterator :
        count = count + 1
        if printfunc is None:
            pprint.pprint( i )
        else:
            printfunc( i )
    print( "Total: %i" % count )
       
    
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
        
        pprint.pprint( batch_query )
        return self._collection.find_one( batch_query )
        
    def find(self, q=None, *args, **kwargs ):
        
        batch_query = Query( { "batchID" : self._audit.getCurrentBatchID() } )
        if q is None:
            query = batch_query
        else:
            query = batch_query.update( q )
            
        if args and kwargs :
            return self._collection.find( query.query(), args, kwargs )
        elif args :
            return self._collection.find( query.query(), args )
        elif kwargs:
            return self._collection.find( query.query(), kwargs )
        else:
            return self._collection.find( query.query())

    
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