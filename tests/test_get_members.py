'''
Created on 6 Jul 2017

@author: jdrumgoole
'''
import unittest
from mugalyser.meetup_api import MeetupAPI
from mugalyser.apikey import get_meetup_key

class Test(unittest.TestCase):

    def setUp(self):
        apikey = get_meetup_key()
        self._api = MeetupAPI( apikey, reshape=True  )
        
    def test_get_member_by_url(self):
        
        members = self._api.get_members( [ "DublinMUG", "London-MongoDB-User-Group"])
        self.assertGreaterEqual( len( list( members )), 2471 )
                                 

if __name__ == "__main__" :
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()