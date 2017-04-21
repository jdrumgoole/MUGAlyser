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
        self._writer = MeetupWriter( self._audit, self._mdb, [ "postgresqlrussia" ] )

    def tearDown(self):
        pass


    def test_get_members(self):
        for _ in self._writer.get_members():
            pass #print( i )
            
    def testProcessMembers(self):
        self._writer.processMembers( nopro=False)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()