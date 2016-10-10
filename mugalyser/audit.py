'''
Created on 30 Sep 2016

@author: jdrumgoole
'''


from datetime import datetime

class AuditDB( object ):
    
    name="audit"
    
    def __init__(self, mdb ):
        self._auditCollection = mdb.database()[ "audit"]
        self._batchID = self._auditCollection.find_one( { "name" : "Current Batch"})
        
        if self._batchID is None:
            self._batchID = {}
            self._batchID[ "name"] = "Current Batch"
            self._batchID[ "ID" ] = 0
            self._auditCollection.insert_one( self._batchID )
    
    def currentBatch(self):
        return self._batchID[ "ID"]
    
    def incrementBatchID(self):
        
        self._batchID[ "ID" ] = self._batchID[ "ID" ]  + 1
        self._batchID[ "timestamp" ] = datetime.now()
        self._auditCollection.update( { "name" : "Current Batch" }, 
                                      { "$set" : { "ID" : self._batchID[ "ID"],
                                                   "timestamp" : self._batchID[ "timestamp" ] }} )
        
    def startBatch(self, trial, doc ):
        self.incrementBatchID()
        self._auditCollection.insert_one( { "batchID" : self._batchID[ "ID" ],
                                            "start"   : datetime.now(),
                                            "trial"   : trial,
                                            "info"    : doc })
        
    def endBatch(self):
        self._auditCollection.update( { "batchID" : self._batchID[ "ID" ]},
                                        { "$set" : { "end"     : datetime.now() }})
        
        
    def auditCollection(self):
        return self._auditCollection
    
    def batchID(self ):
        return self._batchID[ "ID"]
    
