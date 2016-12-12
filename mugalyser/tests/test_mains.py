'''
Created on 12 Dec 2016

@author: jdrumgoole
'''
import unittest
from mugalyser import muginfo_main

class TestMains(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_muginfo_main(self):
        retVal = muginfo_main.main()
        self.assertEqual( retVal, 0 )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()