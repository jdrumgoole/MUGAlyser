'''
Created on 16 Oct 2016

@author: jdrumgoole
'''

from mongodb import MUGAlyserMongoDB
from audit import AuditDB

import unittest


class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB()
        self._audit = AuditDB( self._mdb )
    

    def tearDown(self):
        pass

    def test_incrementID(self):
        curID = self._audit.currentBatchID()
        newID = self._audit.incrementBatchID()
        self.assertEqual( curID + 1, newID )
        newID = self._audit.incrementBatchID()
        self.assertEqual( curID + 2, newID )
        
        
    def test_batch(self):
        
        batchIDs = [ x for x in self._audit.getBatchIDs()]
        
        thisBatchID = self._audit.startBatch( trial=False, doc={ "test" : "doc"})
        
        newBatchIDs = [ x for x in self._audit.getBatchIDs()]
        
        self.assertEqual( len( batchIDs ) + 1, len( newBatchIDs ))
        
        self.assertTrue( thisBatchID in newBatchIDs )
        
        self._audit.endBatch( thisBatchID )
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()