'''
Created on 26 Nov 2016

@author: jdrumgoole
'''
import unittest
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.members import Members
from mugalyser.meetup_writer import MeetupWriter

class Test_members(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( databaseName="TEST_DATA_MUGS")
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
        
    def test_get_many_group_members(self ):
        
        members  = self._members.get_many_group_members( [ "DublinMUG", "London-MongoDB-User-Group"] )
        self.assertGreaterEqual( self._members.count( members ), 2357 )
        
    def test_distinct(self):
        unique_members = self._members.distinct_members()
        self.assertGreaterEqual( len( unique_members ),  46095 )
        #print( len( unique_members ))
        
    def test_get_by_name(self):
        
        jdrumgoole = self._members.get_by_name( "Joe Drumgoole")
        self.assertNotEqual( jdrumgoole, None )
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()