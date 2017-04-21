'''
Created on 12 Oct 2016

@author: jdrumgoole
'''

import pymongo
import bson
import pprint
from mugalyser.generator_utils import coroutine

class BatchWriter(object):
     
    def __init__(self, collection, transformFunc, newDocName, orderedWrites=False ):
         
        self._collection = collection
        self._orderedWrites = orderedWrites
        self._processFunc = transformFunc
        self._newDocName = newDocName
         


    '''
    Intialise coroutine automatically
    '''
    @coroutine 
    def bulkWrite(self, writeLimit=1000 ):
        bulker = None
        try : 
            if self._orderedWrites :
                bulker = self._collection.initialize_ordered_bulk_op()
            else:
                bulker = self._collection.initialize_unordered_bulk_op()
                
            bulkerCount = 0
            
            try :
                while True:
                    doc = (yield)
                    
                    #pprint.pprint( doc )) 
                    bulker.insert( self._processFunc(  self._newDocName, doc  ))
                    bulkerCount = bulkerCount + 1 
                    if ( bulkerCount == writeLimit ):
                        bulker.execute()
                        if self._orderedWrites :
                            bulker = self._collection.initialize_ordered_bulk_op()
                        else:
                            bulker = self._collection.initialize_unordered_bulk_op()
                             
                        bulkerCount = 0
            except GeneratorExit :
                if ( bulkerCount > 0 ) :
                    bulker.execute() 
            except bson.errors.InvalidDocument as e:
                print( "Invalid Document" )
                print( "bson.errors.InvalidDocument: %s" % e )

                raise
        except pymongo.errors.BulkWriteError as e :
            print( "Bulk write error : %s" % e.details )
            raise
        

