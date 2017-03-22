'''
Created on 21 Mar 2017

@author: jdrumgoole
'''
import unittest
import datetime
import pprint

from mugalyser.agg import Agg, AggFormatter
from mugalyser.mongodb import MUGAlyserMongoDB

class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB()
        self._agg = Agg( self._mdb.membersCollection())
        self._formatter = AggFormatter( self._agg )


    def tearDown(self):
        pass


    def test_dateMapField(self):
        
        test_doc = { "a" : 1, "b" : datetime.datetime.now()}
        pprint.pprint( test_doc )
        new_doc = AggFormatter.dateMapField(test_doc, "b" )
        pprint.pprint( new_doc )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()