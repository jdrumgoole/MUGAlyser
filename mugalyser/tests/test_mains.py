'''
Created on 12 Dec 2016

@author: jdrumgoole
'''
import unittest
from mugalyser import muginfo_main, meetup_info_main, mugalyser_main
import sys
import subprocess
import StringIO

class TestMains(unittest.TestCase):


    def setUp(self):
        self._buffer = StringIO.StringIO()

    def tearDown(self):
        pass


    def test_main_help(self):
#         retVal = mugalyser_main.main( [ "-h" ] )
#         self.assertEqual( retVal, 0 )
        result = subprocess.check_call( [ "/usr/local/bin/python", "../muginfo_main.py", "-h" ], 
                                          stdin=None, stdout=self._buffer )
        
        self.assertEqual( result, 0 )
#         retVal = muginfo_main.main( [ "-h" ] )
#         self.assertEqual( retVal, 0 )
#         retVal = meetup_info_main.main( [ "-h" ] )
#         self.assertEqual( retVal, 0 )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()