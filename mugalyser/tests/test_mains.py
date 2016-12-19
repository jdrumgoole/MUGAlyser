'''
Created on 12 Dec 2016

@author: jdrumgoole
'''
import unittest
from mugalyser import muginfo_main, meetup_info_main, mugalyser_main
import sys
import subprocess
import os

class TestMains(unittest.TestCase):


    def setUp(self):
        self._output_filename = "junk"

    def tearDown(self):
        os.unlink( self._output_filename )

    def redirect_cmd(self, programArgs, output_filename ):

        with open( output_filename, 'w') as f:
            return subprocess.check_call( programArgs, stdout=f)

    def test_main_help(self):
        result = self.redirect_cmd( [ "/usr/local/bin/python", "../muginfo_main.py", "-h" ], "junk" )
        self.assertEqual( result, 0 )
        
        result = self.redirect_cmd( [ "/usr/local/bin/python", "../meetup_info_main.py", "-h" ], "junk" )
        self.assertEqual( result, 0 )
        
        result = self.redirect_cmd( [ "/usr/local/bin/python", "../mugalyser_main.py", "-h" ], "junk" )
        self.assertEqual( result, 0 )



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()