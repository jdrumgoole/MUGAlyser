'''
Created on 19 Mar 2017

@author: jdrumgoole
'''
import unittest
from mugalyser.agg import Sorter

class Test_sorter(unittest.TestCase):


    def test_sorter(self):
        a = Sorter()
        self.assertEqual( len( a.sorts()),  1 )
        sort_dict = a.sorts()
        self.assertEqual( len( sort_dict[ "$sort"] ), 0 )
        
    def test_add_sort(self):
        a = Sorter( length="ascending" , width="descending" )
        
        self.assertTrue( "length" in a.sort_fields())
        self.assertTrue( "width" in a.sort_fields())
        #print( a.sort_fields())
        #print( a.sort_directions())
        self.assertTrue( "descending" in a.sort_directions())
        self.assertTrue( "ascending" in a.sort_directions())
        a.add_sort( "up", "ascending" )
        #print( a.sort_items())
        self.assertTrue( ( "up", "ascending" ) in a.sort_items())
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()