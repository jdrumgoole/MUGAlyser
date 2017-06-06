'''
Created on 12 Dec 2016

@author: jdrumgoole
'''
import unittest
import subprocess
import os
import sys

class TestMains(unittest.TestCase):


    def setUp(self):
        root = os.getenv( "MROOT", "")
        if root == "" :
            print( "Environment variable MROOT is not defined" )
            sys.exit( 2 )
        self._binPath = os.path.abspath( os.path.join( root, "bin" ))

    def redirect_cmd(self, programArgs, output_filename ):

        with open( output_filename, 'w') as f:
            return subprocess.check_call( programArgs, stdout=f)

    def test_main_help(self):
        result = self.redirect_cmd( [ "python", os.path.join( self._binPath, "muginfo_main.py" ), "-h" ], "junk" )
        self.assertEqual( result, 0 )
        
        result = self.redirect_cmd( [ "python", os.path.join( self._binPath, "meetup_info_main.py" ), "-h" ], "junk" )
        self.assertEqual( result, 0 )
        
        result = self.redirect_cmd( [ "python", os.path.join( self._binPath, "mugalyser_main.py" ), "-h" ], "junk" )
        self.assertEqual( result, 0 )



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()