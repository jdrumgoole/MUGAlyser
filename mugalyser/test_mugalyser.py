'''
Created on 12 Oct 2016

@author: jdrumgoole
'''
import unittest
from mugalyser.meetup_api import MeetupAPI

from apikey import MEETUP_API_KEY
from pprint import pprint

from mugs import MUGS

class Test(unittest.TestCase):


    def setUp(self):
        self._m = MeetupAPI( MEETUP_API_KEY )
        self._x = None

    def tearDown(self):
        pass


    def test_get_groups(self):
        for i in self._m.get_groups() :
            self._x = i
            
    def test_get_group(self):
        
        group = self._m.get_group( "DublinMUG" )
        self._x = group
        
    def test_get_upcoming_events(self):
        upcoming_events = self._m.get_upcoming_events( "DublinMUG" )
        for i in upcoming_events:
            self._x = i
            
    def test_get_past_events(self):
        past_events = self._m.get_past_events( "DublinMUG" )
        for i in past_events:
            self._x = i

    def test_get_event_attendees(self):
        attendees = self._m.get_event_attendees(62760772, "DublinMUG" )
        for i in attendees:
            self._x = i

    def test_get_attendees(self):
        for attendee in self._m.get_attendees():
            print( attendee )
            
    def test_get_members(self):
        
        members = self._m.get_members( "DublinMUG" )
        for i in members:
            self._x = i
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()