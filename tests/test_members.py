'''
Created on 26 Nov 2016

@author: jdrumgoole
'''
import unittest
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.members import Members
from dateutil.parser import parse

class Test_members(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( uri="mongodb://localhost/TESTMUGS")
        self._members = Members( self._mdb )


    def tearDown(self):
        #self._mdb.client().drop_database( "TEST_MUGS" )
        pass
    
    def test_get_group_size(self):
        
        size  = self._members.get_group_members( "DublinMUG" ).count()
        self.assertGreaterEqual( size, 826 )

    def test_get_all_members( self ):
        cursor = self._members.get_all_members()
        #print( cursor.count())
        self.assertGreaterEqual( cursor.count(), 826 )
        
        cursor = self._members.get_all_members()
        #print( cursor.count())
        self.assertGreaterEqual( cursor.count(), 826 )
        
    def test_get_many_group_members(self ):
        
        members  = self._members.get_many_group_members( [ "DublinMUG", "London-MongoDB-User-Group"] )
        self.assertGreaterEqual( self._members.count( members ), 2357 )
        
    def test_get_group_members(self ):
        members  = self._members.get_group_members( "DublinMUG" )
        self.assertGreaterEqual( len( list( members)), 830 )
        #self._members.count_print( members )

        
    def test_distinct(self):
        unique_members = self._members.distinct_members()
        self.assertGreaterEqual( len( unique_members ),  46095 )
        #print( len( unique_members ))
        
    def test_get_by_name(self):
        
        jdrumgoole = self._members.get_by_name( "Joe Drumgoole")
        self.assertNotEqual( jdrumgoole, None )
        
    def test_get_by_date_range(self ):
        
        start = parse( "1-Jan-2009, 00:01" )
        end = parse( "31-Dec-2009 11:59" )
        members = self._members.get_by_join_date( start , end )
        all_members = list( members )
        self.assertEqual( len( all_members), 58 )


    def test_joined_by_year(self):
        joined = self._members.joined_by_year()
        total = 0
        for i in joined :
            total = total + i[ "total_registered"]
            
        members = self._members.get_all_members()
        self.assertEqual( len( list( members )), total )
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()