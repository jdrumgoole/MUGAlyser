'''
Created on 6 Jan 2017

@author: jdrumgoole
'''
import unittest
from mugalyser.mugdata import MUGData
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.mugdata import MUGData, printCursor
class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( uri="mongodb://localhost/TESTMUGS" )
        self._mugData = MUGData( self._mdb, "groups")


    def tearDown(self):
        pass


    def testFind(self):
        cursor = self._mugData.find( {  "group.country" : { "$in" : [ 'USA' ] }})
        self.assertEqual( len( list( cursor )), 41 )

    def testCombine(self):
        pass
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()