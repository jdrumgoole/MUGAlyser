'''
Created on 22 Oct 2017

@author: jdrumgoole
'''
import unittest
import pymongo
from mugalyser.analytics import MUG_Analytics
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
import os

class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB()
        self._analytics = MUG_Analytics( self._mdb )

    def tearDown(self):
        pass


    def testName(self):
        pass


    def test_groups(self):
        filename = self._analytics.get_groups( [ "DublinMUG" ], "test_groups.json")
        self.assertTrue( os.path.isfile( filename ))
        audit = Audit( self._mdb )
        self.assertTrue( audit.isProBatch( self._analytics.get_batch_ID()))
        os.unlink( filename )
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()