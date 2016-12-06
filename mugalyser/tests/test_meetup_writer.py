'''
Created on 5 Dec 2016

@author: jdrumgoole
'''
import unittest

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.meetup_writer import MeetupWriter
from mugalyser.meetup_api import MeetupAPI
from mugalyser.apikey import get_meetup_key
from mugalyser.audit import Audit
from mugalyser.version import __version__, __programName__


class Test_meetup_writer(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( databaseName="TEST_DATA_MUGS")

        self._audit = Audit( self._mdb )

    def tearDown(self):
        # we don't remove the database because this test data is reused across
        # test runs.
        pass

    def _get_data(self, writer ):
        batchID = self._audit.startBatch( { "args"    : None, 
                                           "version" : __programName__ + " " + __version__ },
                                           trial = False,
                                           apikey=get_meetup_key())
        
        writer.capture_complete_snapshot()
        
        self._audit.endBatch( batchID )
        
    def test_get_data_unordered(self):
        self._writer = MeetupWriter( self._mdb, MeetupAPI(), unordered = True )
        self._get_data( self._writer)
        
    def xtest_get_data_ordered(self):
        self._writer = MeetupWriter( self._mdb, MeetupAPI(), unordered = False )
        self._get_data( self._writer )



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()