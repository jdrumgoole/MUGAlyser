'''
Created on 12 Oct 2016

@author: jdrumgoole
'''

import pymongo

class BatchWriter(object):
     
    def __init__(self, collection, auditCollection, orderedWrites=False, writeLimit=200 ):
         
        self._collection = collection
        self._auditCollection = auditCollection
        self._orderedWrites = orderedWrites
        self._writeLimit = writeLimit
         
        
    def bulkWrite(self, sourceGenerator, func, name ):
        bulker = None
        try : 
            if self._orderedWrites :
                bulker = self._collection.initialize_ordered_bulk_op()
            else:
                bulker = self._collection.initialize_unordered_bulk_op()
                
            bulkerCount = 0
            for doc in sourceGenerator :
                
                #print( "dict: %s" % dictEntry ) 
                bulker.insert( func(  name,  doc  ))
                bulkerCount = bulkerCount + 1 
                if ( bulkerCount == self._writeLimit ):
                    bulker.execute()
                    if self._orderedWrites :
                        bulker = self._collection.initialize_ordered_bulk_op()
                    else:
                        bulker = self._collection.initialize_unordered_bulk_op()
                         
                    bulkerCount = 0
             
            if ( bulkerCount > 0 ) :
                bulker.execute()

 
        except pymongo.errors.BulkWriteError as e :
            print( "Bulk write error : %s" % e.details )
            raise
        
        return  bulker
