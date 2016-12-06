'''
Created on 5 Dec 2016

@author: jdrumgoole
'''
import unittest

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.batchwriter import BatchWriter

class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( databaseName="TEST_BATCHWRITER")


    def tearDown(self):
        #self._mdb.client().drop_database( "TEST_BATCHWRITER" )
        pass 
    @unittest.skip
    def test_batchwriter(self):
        collection = self._mdb.database()[ "TEST_WRITE"]
        bwriter = BatchWriter( collection, lambda x,y: y, "test" )
        writer = bwriter.bulkWrite()
        for i in range( 1000000 ) :
            print( "Writing: %i"  % i)
            writer.send( { "value" : i })
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_batchwriter']
    unittest.main()