'''
Created on 6 Jan 2017

@author: jdrumgoole
'''
import unittest
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.mugdata import MUGData
class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( uri="mongodb://localhost/TESTMUGS" )
        self._mugData = MUGData( self._mdb, "groups")


    def tearDown(self):
        pass

    def testFindSimple(self):
        cursor = self._mugData.find( { "group.country" : "USA" })
        self.assertEqual( len( list( cursor )), 82 )

    def testFind(self):
        cursor = self._mugData.find( {  "group.country" : { "$in" : [ "USA", "United Kingdom" ] }})
        self.assertGreaterEqual( len( list( cursor )), 96 )

    def testCombine(self):
        pass
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()