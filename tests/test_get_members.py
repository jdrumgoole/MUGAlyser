'''
Created on 6 Jul 2017

@author: jdrumgoole
'''
import unittest
from mugalyser.meetup_api import MeetupAPI
from mugalyser.apikey import get_meetup_key
from mugalyser.meetup_request import MeetupRequest
class Test(unittest.TestCase):

    def setUp(self):
        apikey = get_meetup_key()
        self._api = MeetupAPI( apikey, reshape=True  )

    def test_logging(self):
        r = MeetupRequest()
        
    def xtest_get_member_by_url(self):
        
        members = self._api.get_members( [ "DublinMUG", "London-MongoDB-User-Group"])
        count = 0
        for i in members:
            count = count + 1 
            print ( "%i. %s" % ( count, i[ "name"]))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()