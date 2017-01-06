'''
Created on 8 Dec 2016

@author: jdrumgoole
'''
import unittest

from mugalyser.events import PastEvents, UpcomingEvents
from mugalyser.mongodb import MUGAlyserMongoDB

class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( uri="mongodb://localhost/TESTMUGS" )
        self._past = PastEvents( self._mdb )
        self._upcoming = UpcomingEvents( self._mdb )

    def tearDown(self):
        pass


    def test_get_group_events(self):
        events = self._past.get_group_events( "DublinMUG"  )
        self.assertGreaterEqual( len( list( events )), 29 )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()