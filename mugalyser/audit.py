'''
Created on 30 Sep 2016

The Audit collection keeps track of all the runs of the MUGALyser tool.
There is a master document which tracks the current batch. Here is an
example.

{  "name"          : "Current Batch"
   "currentID"     : 13
   "batchID"       : 0
   "schemaVersion" : 0.8
   "timestamp"     : October 10, 2016 9:16 PM }
   
Name is used to identify the document.
currentID is the current batch ID. i.e. the last batch to be processed.
Timestamp tells us the date and time on which that batch started being 
processed.

batchID allows us to identify the CurrentBatch record and as batchID is
indexed this is a fast way to find the CurrentBatch record.

If we now look at the corresponding batch document.

{ "batchID" :  13
  "start"    : October 10, 2016 9:16 PM
  "info"     : { "args"  : { ... }
                 "MUGS" : { ... }
                }
   "version" : "mugalyser_main.py 0.7 beta"
   "trial"   : false
   "end"     : October 10, 2016 9:42 PM
}

This tells us that this is the data for batchID 13.

The run started at "start" time. Which corresponds to the timestamp
in "CurrentBatch" above.

The info field contains the command line arguments and the list of MUGS
that were processed. The information is elided here for brevity (do take a look
at the schema after a run).

"version" is the version of the MUGAlyser program that captured this data.

"trial" : Indicates this was a trial run so no data was captured (used
for testing).

"end" : Indicates when the run completed. An incomplete run will not 
have an end date field.

@author: jdrumgoole
'''

from datetime import datetime
from version import __version__

from apikey import get_meetup_key
class Audit( object ):
    
    name="audit"
    
    def __init__(self, mdb ):
        self._auditCollection = mdb.auditCollection()
        self._currentBatch = self._auditCollection.find_one( { "name" : "Current Batch"})
        
        if self._currentBatch is None:
            self._currentBatch = {}
            self._currentBatch[ "name"] = "Current Batch"
            self._currentBatch[ "currentID" ] = 0
            self._currentBatch[ "batchID" ] = 0
            self._currentBatch[ "schemaVersion" ] = __version__
            self._auditCollection.insert_one( self._currentBatch )
        else:
            # Migrate schema from version 0.7 to 0.8
            if self._currentBatch.has_key( "ID" ):
                self._auditCollection.update( { "_id" : self._currentBatch[ "_id"]},
                                              { "$rename" : { "ID" : "currentID" }})
                
                curid = self._currentBatch[ "ID"]
                del self._currentBatch[ "ID"]
                self._currentBatch[ "currentID" ]= curid
                
            if not "batchID" in self._currentBatch :
                self._auditCollection.update( { "_id" : self._currentBatch[ "_id"]},
                                              { "$set" : { "batchID" : 0 }})
            
                self._currentBatch[ "batchID" ] = 0
            
            self._auditCollection.update( { "_id" : self._currentBatch[ "_id"]},
                                          { "$set" : { "schemaVersion" : __version__  }})


    def collection(self):
        return self._auditCollection
        
    def insertTimestamp( self, doc, ts=None ):
        if ts :
            doc[ "timestamp" ] = ts
        else:
            doc[ "timestamp" ] = datetime.utcnow()
            
        return doc
    
    def addTimestamp( self, name, doc, ts=None ):
    
        tsDoc = { name : doc, "timestamp" : None, "batchID": self.getCurrentBatchID()}
        return self.insertTimestamp( tsDoc, ts )
    
    def addInfoTimestamp(self, doc, ts=None ):
        return self.addTimestamp( "info", doc, ts )
    
    def addMemberTimestamp(self, doc, ts=None ):
        return self.addTimestamp( "member", doc, ts )
    
    def addEventTimestamp(self, doc, ts=None ):
        return self.addTimestamp( "event", doc, ts )
    
    def addGroupTimestamp(self, doc, ts=None ):
        return self.addTimestamp( "group", doc, ts )
    
    def addAttendeeTimestamp(self, doc, ts=None ):
        return self.addTimestamp( "attendee", doc, ts )
    
    def getBatchIDs(self):
        cursor = self._auditCollection.find( { "batchID" : { "$exists" : 1 }}, { "_id" : 0, "batchID" : 1})
        for i in cursor:
            if i[ "batchID"] == 0 :
                continue
            yield i[ 'batchID' ]
            
    def incrementBatchID(self):
        #
        # We can have multiple batches running in parallel as long as each has a unique
        # batch ID. Find And Modify ensures that each batch ID is unique.
        curBatch = self._auditCollection.find_and_modify( { "name" : "Current Batch" },
                                                          update= { "$inc" : { "currentID" : 1 },
                                                                    "$set" : { "timestamp" : datetime.now() }},
                                                         new = True )
        
        return curBatch[ "currentID" ]
#         self._currentBatch[ "currentID" ] = self.getCurrentBatchID()  + 1
#         self._currentBatch[ "timestamp" ] = datetime.now()
#         self._auditCollection.update( { "name" : "Current Batch" }, 
#                                       { "$set" : { "currentID" : self._currentBatch[ "currentID"],
#                                                    "timestamp" : self._currentBatch[ "timestamp" ] }} )
        
    def startBatch(self, trial, doc, apikey = get_meetup_key()):
        thisBatchID = self.incrementBatchID()
        self._auditCollection.insert_one( { "batchID" : thisBatchID,
                                            "start"   : datetime.now(),
                                            "trial"   : trial,
                                            "end"     : None,
                                            "apikey"  : apikey,
                                            "info"    : doc })
        
        return thisBatchID
        
    def endBatch(self, batchID ):
        self._auditCollection.update( { "batchID" : batchID },
                                      { "$set" : { "end" : datetime.now() }})
        
        
    def auditCollection(self):
        return self._auditCollection
    
    def getLastBatchID(self):
        curBatch = self._auditCollection.find_one( { "name" : 'Current Batch'} )
        return curBatch[ "currentID"] - 1
    
    def getCurrentBatchID(self ):
        curBatch = self._auditCollection.find_one( { "name" : 'Current Batch'} )
        return curBatch[ "currentID"]
    