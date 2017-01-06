'''
Created on 5 Dec 2016

@author: jdrumgoole
'''
import unittest

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.groups import Groups
import pprint

class Test_groups(unittest.TestCase):


    def setUp(self):
        self._mdb = MUGAlyserMongoDB( uri="mongodb://localhost/MUGS" )
        self._groups = Groups( self._mdb)


    def tearDown(self):
        #self._mdb.client().drop_database( "TEST_MUGS" )
        pass

    def test_get_groups(self):
        g = self._groups.get_group( "DublinMUG")
        self.assertEqual( g[ "group"][ "urlname"], "DublinMUG" )
        
    def testGroups(self):
        groups = self._groups.get_all_groups()
        self.assertEqual( len( [ x for x in groups ]), 114 )

        groups = self._groups.get_all_groups( region=[ 'USA'] )
        
    def test_get_country_urlnames(self ):
        urls = self._groups.get_country_group_urlnames()
        self.assertGreaterEqual( len( urls ), 41 )
        self.assertTrue( "nyccpp" in urls )
        
    def test_get_region_urlnames(self):
        pass
        eu_groups = self._groups.get_region_group_urlnames()
        self.assertEqual( len( eu_groups ), 40 )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()