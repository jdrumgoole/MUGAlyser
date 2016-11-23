'''
Created on 12 Oct 2016

@author: jdrumgoole
'''

import pymongo
from coroutine import coroutine

class BatchWriter(object):
     
    def __init__(self, collection, auditCollection, transformFunc, newDocName, orderedWrites=False, writeLimit=200 ):
         
        self._collection = collection
        self._orderedWrites = orderedWrites
        self._writeLimit = writeLimit
        self._processFunc = transformFunc
        self._newDocName = newDocName
         


    '''
    Intialise corountine by calling next
    '''
    @coroutine 
    def bulkWrite(self ):
        bulker = None
        result = None
        inserted = 0
        try : 
            if self._orderedWrites :
                bulker = self._collection.initialize_ordered_bulk_op()
            else:
                bulker = self._collection.initialize_unordered_bulk_op()
                
            bulkerCount = 0
            
            try :
                while True:
                    doc = (yield)
                    
                    #print( "dict: %s" % dictEntry ) 
                    bulker.insert( self._processFunc(  self._newDocName, doc  ))
                    bulkerCount = bulkerCount + 1 
                    if ( bulkerCount == self._writeLimit ):
                        bulker.execute()
                        if self._orderedWrites :
                            bulker = self._collection.initialize_ordered_bulk_op()
                        else:
                            bulker = self._collection.initialize_unordered_bulk_op()
                             
                        bulkerCount = 0
            except GeneratorExit :
                if ( bulkerCount > 0 ) :
                    bulker.execute() 
        except pymongo.errors.BulkWriteError as e :
            print( "Bulk write error : %s" % e.details )
            raise
