'''
Created on 8 Dec 2016

@author: jdrumgoole
'''
import unittest

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.attendees import Attendees

class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( uri="mongodb://localhost/TESTMUGS")
        self._attendees = Attendees( self._mdb )



    def tearDown(self):
        pass


    def test_get_attendees(self):
        
        attendees = self._attendees.find()
        self.assertGreaterEqual( len( list( attendees )), 1306 )
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()