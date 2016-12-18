'''
Created on 16 Oct 2016

@author: jdrumgoole
'''

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit

import unittest

class Test_audit(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( databaseName="TEST_MUGS" )
        self._audit = Audit( self._mdb )
    

    def tearDown(self):
        #self._mdb.client().drop_database( "TEST_MUGS" )
        pass
    
    #@unittest.skip
    def test_incrementID(self):
        batchID = self._audit.incrementBatchID()
        curID = self._audit.getCurrentBatchID()

        self.assertEqual( batchID, curID )
        newID = self._audit.incrementBatchID()
        self.assertEqual( batchID + 1, newID )
        
    def test_batch(self):
        
        batchIDs = [ x for x in self._audit.getBatchIDs()]
        
        thisBatchID = self._audit.startBatch( doc={ "test" : "doc"}, trial=False)
        
        newBatchIDs = [ x for x in self._audit.getBatchIDs()]
        
        self.assertEqual( len( batchIDs ) + 1, len( newBatchIDs ))
        
        self.assertTrue( thisBatchID in newBatchIDs )
        
        self._audit.endBatch( thisBatchID )
        
    #@unittest.skip
    def test_IDs(self):

        self._id = MUGAlyserMongoDB( databaseName="TEST_IDS" )
        self._audit = Audit( self._id )
        self.assertRaises( ValueError,self._audit.getCurrentBatchID )
        self.assertRaises( ValueError, self._audit.getLastBatchID )
        self.assertFalse( self._audit.inBatch())
        batchID = self._audit.startBatch( {} )
        self.assertTrue( self._audit.inBatch())
        self.assertEquals( 1, self._audit.getCurrentBatchID())
        self._audit.endBatch( batchID )

        batch = self._audit.getBatch( batchID )
        self.assertTrue( "start" in batch )
        self.assertTrue( "end" in batch )
        self.assertTrue( "info" in batch )
        self.assertTrue( "batchID" in batch )
        self.assertFalse( self._audit.incomplete( batchID ))
        
        batchID = self._audit.startBatch( {} )
        self.assertTrue( self._audit.inBatch())
        self.assertEquals( 2, self._audit.getCurrentBatchID())
        self._audit.endBatch( batchID )
        self.assertFalse( self._audit.inBatch())
        self._mdb.client().drop_database( "TEST_IDS" )
        
    #@unittest.skip
    def test_start_end_batch(self):
        
        batchID = self._audit.startBatch({})
        self.assertTrue( self._audit.incomplete( batchID ))
        self._audit.endBatch( batchID )
        self.assertFalse( self._audit.incomplete( batchID ))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()