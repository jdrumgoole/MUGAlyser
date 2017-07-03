'''
The audit collection is used to track a batch process that has a distinct start and finish.
Each process has a start and end document that is linked by a batchID. BatchIDs are unique.

Batch creation (specifically batch ID increment) is protected by a lock to make it thread safe.

An invalid batch is any batch with a start batch and no correspoding end batch. Batch documents
are never updated so that the atomic properties of document writes ensure that batch creation
and batch completion are all or nothing affairs.

Start Batch Document
{ "batchID" :  13
  "start"    : October 10, 2016 9:16 PM
  "info"     : { "args"  : { ... }
                 "MUGS" : { ... }
                }
   "version" : "mugalyser_main.py 0.7 beta"
}

End Batch Document
{ "batchID"  :  13
  "end"      : October 10, 2016 9:20 PM
}

There is an index on batchID.


'''

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
from threading import Lock

class Audit( object ):
    
    name="audit"
    
    def __init__(self, mdb ):
        
        self._lock = Lock()
        self._mdb = mdb
        self._auditCollection = mdb.auditCollection()
        self._open_batch_count = 0
        
    def collection(self):
        return self._auditCollection
        
    def mdb( self ):
        return self._mdb

    
    def isProBatch(self, ID ):
        doc = self.get_batch( ID )

        return ( doc.has_key( "info") and 
                 doc[ "info"].has_key( "pro_account" ) and 
                 ( doc[ "info" ][ "pro_account"] == True ))


    
    def getBatchIDs(self):
        cursor = self._auditCollection.find( { "batchID" : { "$exists" : 1 }}, { "_id" : 0, "batchID" : 1})
        for i in cursor:
            if i[ "batchID"] == 0 :
                continue
            yield i[ 'batchID' ]
        
    def start_batch(self, doc, name=None ):

        with self._lock :
            last_id = self.get_last_batch_id()
            if last_id is None :
                last_id = 0
            new_batch_id = last_id + 1
            self._open_batch_count = self._open_batch_count + 1
            self._auditCollection.insert_one( { "batchID" : new_batch_id,
                                                "start"   : datetime.utcnow(),
                                                "name"    : name,
                                                "info"    : doc })
        
        return new_batch_id
    
    def end_batch(self, batchID ):
            
        if not self.is_batch( batchID):
            raise ValueError( "BatchID does not exist: %s" % batchID )
        
        self._auditCollection.insert_one( { "batchID" : batchID,
                                            "end"     : datetime.utcnow()})
        self._open_batch_count = self._open_batch_count - 1
        return batchID   
    
    def in_batch(self):
        with self._lock :
            return self._open_batch_count > 0 
             
    def get_batch(self, batchID ):
        batch = self._auditCollection.find_one( { "batchID" : batchID })
        if batch is None:
            raise ValueError( "BatchID does not exist: %s" % batchID )
        
        return batch
    
    def is_batch(self, batchID ):
        return self._auditCollection.find_one( { "batchID" : batchID })
    
    def complete(self, batchID ):
        if self._auditCollection.find_one( { "batchID" : batchID } ) is None:
            raise ValueError( "BatchID does not exist: %s" % batchID )
        else:
            return self._auditCollection.find_one( { "batchID" : batchID, "end" : { "$exists" : 1 }})
        
        
    def incomplete(self, batchID ):
        return not self.complete( batchID )
        

        
    def auditCollection(self):
        return self._auditCollection
    
#     def getLastBatchID(self):
#         curBatch = self._auditCollection.find_one( { "name" : 'Current Batch'} )
#         if curBatch[ "currentID" ] < 2 :
#             raise ValueError( "No valid last batch")
#         else:
#             return curBatch[ "currentID"] - 1
    
    def get_batches(self):
        
        batches = self._auditCollection.find( { "batchID" : { "$exists" : 1 },
                                                "start"   : { "$exists" : 1 }}).sort( "start", pymongo.DESCENDING )
        for i in batches:
            yield i
            
    def get_batch_ids(self):
        for i in self.get_batches():
            yield i[ "batchID" ]
            
            
    def get_last_batch_id(self):
        '''
        There may be incomplete batches int he mix. We make sure the next batch ID we select
        does not overlap with an incomplete batch ID.
        '''
        
        results = self.get_batch_ids()
        
        for i in results :
            return i
        
            
    def get_valid_batches( self, start=None, end=None):

        if start and not isinstance( start, datetime ):
            raise ValueError( "start is not a datetime object")
        if end and not isinstance( end, datetime ):
            raise ValueError( "end is not a datetime object")
        
   
        batches = self._auditCollection.find( { "end" : { "$exists" : 1 }}).sort( "end", pymongo.DESCENDING )
         
        for i in batches:
            batch_date = i[ 'end']
             
            if start and end :
                if batch_date >= start and batch_date <= end :
                    yield i
            elif start:
                if batch_date >= start:
                    yield i
            elif end:
                if batch_date <= end :
                    yield i
            else:
                yield i
            
    def get_valid_batch_ids( self ):
        for i in self.get_valid_batches():
            yield i[ "batchID" ]
            
    def get_last_valid_batch_id(self):
        ids = self.get_valid_batch_ids()
        for i in ids:
            return i
        
    