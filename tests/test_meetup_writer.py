'''
Created on 20 Apr 2017

@author: jdrumgoole
'''
import unittest
from mugalyser.meetup_writer import MeetupWriter
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB("mongodb://localhost:27017/TESTMUGS")
        self._audit = Audit( self._mdb )
        batchID = self._audit.startBatch({ "test" : 1} )
        self._writer = MeetupWriter( self._audit, self._mdb, [ "postgresqlrussia" ] )
        self._audit.endBatch(batchID)

    def tearDown(self):
        pass


    def test_get_members(self):
        for _ in self._writer.get_members():
            pass #print( i )
            
    def testProcessMembers(self):
        self._writer.processMembers()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()