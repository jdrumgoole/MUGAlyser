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
from _sqlite3 import Cursor

class Test(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB()
        self._agg = Agg( self._mdb.membersCollection())
        
    def tearDown(self): 
        pass

    def testFormatter(self):
        self._agg.addMatch( { "member.member_name" : "Joe Drumgoole"})
        #print( "agg: %s" % self._agg )
        self._agg.addProject( { "member.member_name" : 1,
                                "_id" : 0,
                                "member.join_time" : 1,
                                "member.city" : 1,
                             })
        cursor = self._agg.aggregate()
        prefix="agg_test_"
        filename="JoeDrumgoole"
        ext = "json"
        self._formatter = CursorFormatter( cursor, prefix=prefix, name=filename, ext=ext)
        self._formatter.output( fieldNames=[ "member.member_name", "member.join_time", "member.city"], datemap=[ "member.join_time"] )
        self.assertTrue( os.path.isfile( prefix + filename + "." + ext ))
        os.unlink( prefix + filename + "." + ext )
        
    def testFieldMapper(self):
        
        doc = { "a" : "b"}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a' ])
        self.assertTrue( newdoc.has_key( "a" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f" }
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c' ])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" )) 
        self.assertFalse( newdoc.has_key( "e" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x"}}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w"])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" ))
        self.assertTrue( newdoc.has_key( "z" ))
        self.assertTrue( newdoc["z"].has_key( "w" ))
        self.assertFalse( newdoc.has_key( "e" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x",
                        "y" : "p" }}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w"])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" ))
        self.assertTrue( newdoc.has_key( "z" ))
        self.assertTrue( newdoc["z"].has_key( "w" ))
        self.assertFalse( newdoc.has_key( "e" ))
        self.assertFalse( newdoc[ 'z' ].has_key( "y" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x",
                        "y" : "p" },
                "g" : { "h" : "i",
                        "j" : "k" }}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w", "g.j"])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" ))
        self.assertTrue( newdoc.has_key( "z" ))
        self.assertTrue( newdoc["z"].has_key( "w" ))
        self.assertFalse( newdoc.has_key( "e" ))
        self.assertFalse( newdoc[ 'z' ].has_key( "y" ))
        self.assertTrue( newdoc.has_key( "g" ))
        self.assertTrue( newdoc['g'].has_key( "j"))
        self.assertFalse( newdoc['g'].has_key( "h"))
        
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
        #pprint.pprint( test_doc )
        new_doc = CursorFormatter.dateMapField(test_doc, "b" )
        #pprint.pprint( new_doc )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()