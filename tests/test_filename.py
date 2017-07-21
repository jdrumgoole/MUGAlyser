'''
Created on 20 Jul 2017

@author: jdrumgoole
'''
import unittest
from mugalyser.analytics import Filename

class Test(unittest.TestCase):


    def test_Filename(self):
        n = Filename( "pre", "name", "suf", "ext")
        self.assertEqual( str( n ),  "prenamesuf.ext" )
        
        n.name( "new")
        self.assertEqual( str( n ),  "prenewsuf.ext" )

        n = Filename( "pre", "name", "suf", ".ext")
        self.assertEqual( str( n ),  "prenamesuf.ext" )
        
        n = Filename( "pre", "-", "suf", "ext")
        self.assertEqual( str( n ),  "-" )

        n = Filename( "pre", None, "suf", "ext")
        self.assertEqual( str( n ),  "-" )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()