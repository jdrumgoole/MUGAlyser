'''
Created on 21 Mar 2017

@author: jdrumgoole
'''
import unittest
import datetime
import pprint
import os

from mugalyser.agg import Agg, CursorFormatter, NestedDict
from mugalyser.mongodb import MUGAlyserMongoDB

class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB()
        self._agg = Agg( self._mdb.membersCollection())
        
    def tearDown(self):
        pass


    def testFormatter(self):
        self._agg.match( { "member.member_name" : "Joe Drumgoole"})
        self._agg.project( { "member.member_name" : 1,
                             "_id" : 0,
                             "member.join_time" : 1,
                             "member.city" : 1,
                             })
        cursor = self._agg.aggregate()
        prefix="agg_test_"
        filename="JoeDrumgoole"
        ext = "json"
        self._formatter = CursorFormatter( cursor, prefix=prefix, name=filename, ext=ext)
        self._formatter.output( fieldNames=[ "member.member_name", "member.join_time", "member.city"], datemap=[ "member.join_time "] )
        self.assertTrue( os.path.isfile( prefix + filename + "." + ext ))
        os.unlink( prefix + filename + "." + ext )
        
    def testNestedDict(self):
        d = NestedDict( {})
        self.assertFalse( d.has_key( "hello"))
        d.set_value( "hello", "world")
        self.assertTrue( d.has_key( "hello"))
        self.assertEqual( d.get_value( "hello" ), "world" )
        self.assertRaises( KeyError, d.get_value, "Bingo" )
        
        d.set_value( "member.name", "Joe Drumgoole")
        self.assertEqual( d.get_value( "member"), { "name" : "Joe Drumgoole" })
        
    def test_dateMapField(self):
        
        test_doc = { "a" : 1, "b" : datetime.datetime.now()}
        pprint.pprint( test_doc )
        new_doc = CursorFormatter.dateMapField(test_doc, "b" )
        pprint.pprint( new_doc )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()