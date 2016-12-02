'''
Created on 26 Nov 2016

@author: jdrumgoole
'''
import unittest
from mongodb import MUGAlyserMongoDB
from members import Members
class TestMembers(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB()
        self._members = Members( self._mdb )


    def tearDown(self):
        pass


    def test_get_group_size(self):
        
        size  = self._members.get_group_members( "DublinMUG" ).count()
        self.assertGreaterEqual( size, 826 )

    def test_get_all_members( self ):
        cursor = self._members.get_all_members()
        self.assertGreaterEqual( cursor.count(), 51103 )
        
    def test_get_many_group_members(self ):
        
        members  = self._members.get_many_group_members( [ "DublinMUG", "London-MongoDB-User-Group"] )
        self.assertGreaterEqual( self._members.count( members ), 2357 )
        
    def test_distinct(self):
        unique_members = self._members.distinct_members()
        self.assertGreaterEqual( len( unique_members ),  46126 )
        print( len( unique_members ))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()