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

import pymongo
from datetime import datetime
from mugalyser.version import __programName__, __version__, __schemaVersion__
from mongodb_utils.agg import Agg, Sorter
from mugalyser.apikey import get_meetup_key

class Audit( object ):
    
    name="audit"
    
    def __init__(self, mdb ):
        
        self._mdb = mdb
        self._auditCollection = mdb.auditCollection()
        self._currentBatch = self._auditCollection.find_one( { "name" : "Current Batch"})
        
        if self._currentBatch is None:
            self._currentBatch = {}
            self._currentBatch[ "name"] = "Current Batch"
            self._currentBatch[ "currentID" ] = 0
            self._currentBatch[ "batchID" ] = 0
            self._currentBatch[ 'valid'] = False
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
                                          { "$set" : { "schemaVersion" : __schemaVersion__  }})

        self._currentBatchID = None
        
    def collection(self):
        return self._auditCollection
        
    def mdb( self ):
        return self._mdb
    
    def inBatch(self):
        return self._currentBatchID
    
    def isProBatch(self, ID ):
        doc = self.getBatch( ID )

        return ( doc.has_key( "info") and 
                 doc[ "info"].has_key( "pro_account" ) and 
                 ( doc[ "info" ][ "pro_account"] == True ))
              
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
        
    def startBatch(self, doc, name=None ):
        thisBatchID = self.incrementBatchID()
        
        if name is None :
            name = "Standard Batch: %i" % thisBatchID
            
        self._auditCollection.insert_one( { "batchID" : thisBatchID,
                                            "start"   : datetime.now(),
                                            "end"     : None,
                                            "name"    : name,
                                            "info"    : doc })
        
        self._currentBatchID = thisBatchID
        
        return thisBatchID
        
    def getBatch(self, batchID ):
        return self._auditCollection.find_one( { "batchID" : batchID })
    
    def incomplete(self, batchID ):
        return self.getBatch( batchID )[ "end" ] == None
        
    def endBatch(self, batchID ):
        self._auditCollection.update( { "batchID" : batchID },
                                      { "$set" : { "end"  : datetime.now(), 
                                                  "valid" : True }})
        
        self._currentBatchID = None
        
    def auditCollection(self):
        return self._auditCollection
    
#     def getLastBatchID(self):
#         curBatch = self._auditCollection.find_one( { "name" : 'Current Batch'} )
#         if curBatch[ "currentID" ] < 2 :
#             raise ValueError( "No valid last batch")
#         else:
#             return curBatch[ "currentID"] - 1
    
    def getCurrentValidBatchID( self ):
        '''
        A Valid Batch record has a start and a end field that are both types.
        It also has "valid" field set to true.
        '''
        cur_batch = self._auditCollection.find( { "start" : { "$type" : "date" },
                                                  "end"   : { "$type" : "date" }} ) #17 BSON type for timestamp
        
        results = cur_batch.sort( "batchID", pymongo.DESCENDING ).limit( 1 )
        
        if results is None :
            raise ValueError( "No current valid batch ID" )
        else:
            try :
                x= results.next()[ "batchID"]
                return x
            except StopIteration :
                raise ValueError( "Iterator returned no results")
            
    def getCurrentValidBatches( self, start=None, end=None ):
        
        agg = Agg( self._auditCollection )
        agg.addMatch({ "apikey" : get_meetup_key(),
                       "end"    : { "$ne" : None },
                       "trial"  : False }  )
        
        agg.addRangeMatch( "start", start, end)
        agg.addSort( Sorter( batchID = pymongo.DESCENDING ))
        
#         cursor = self._auditCollection.find( { "apikey" : get_meetup_key(),
#                                                "end"    : { "$ne" : None },
#                                                "trial"  : False } ).sort( "batchID", pymongo.DESCENDING )
                                         
        return agg

            
    def getCurrentValidBatchIDs( self ):
        for i in self.getCurrentValidBatches().aggregate():
            yield i[ "batchID" ]
            
    def getCurrentBatch( self ) :
        return self._auditCollection.find_one( { "name" : 'Current Batch'} )
    
    def getCurrentBatchID(self ):
        if self._currentBatchID :
            return self._currentBatchID
        else:
            curBatch = self._auditCollection.find_one( { "name" : 'Current Batch'} )
            
            if curBatch[ "currentID" ] == 0 :
                raise ValueError( "No batches in database" )
            else:
                return curBatch[ "currentID" ]
    