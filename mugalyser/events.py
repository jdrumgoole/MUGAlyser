'''
Created on 31 Oct 2016

@author: jdrumgoole
'''

from audit import Audit
from mugalyser import MUGAlyser
from requests import HTTPError
import logging
from mugs import MUGS
from feedback import Feedback

class Events(object):
    '''
    classdocs
    '''
    
    def __init__(self, apikey, auditor, eventCollection ):
        '''
        Constructor
        '''
        self._events = eventCollection
        self._audit = auditor
        self._mlyser = MUGAlyser( apikey )
        self._eventCount = 0
        self._feedback = Feedback()
        
    def get_events(self, url_name ):
        
        eventCount = 0 
        try:
            self._feedback.output( "Get %s for: %s" % ( self.__class__.__name__, url_name ))
            events = self._mlyser.get_upcoming_events( url_name )
            
            for i in events:
                self._events.insert_one( self._audit.addEventTimestamp( i ))
                eventCount = eventCount + 1 
                
            return eventCount
        
        except HTTPError, e :
            logging.error( "Stopped upcoming events request: %s : %s", url_name, e )
            raise
        
    def get_all_events(self, groups=None ):
        
        if groups is None:
            groups = MUGS
            
        for i in groups:
            self._eventCount = self._eventCount + self.get_events( i )
            
        return self._eventCount
        
class PastEvents(Events):
    '''
    classdocs
    '''


    def __init__(self, mdb, apikey ):
        '''
        Constructor
        '''
        super( PastEvents, self ).__init__( apikey, Audit( mdb ), mdb.pastEventsCollection())
        
class UpcomingEvents(Events):
    '''
    classdocs
    '''


    def __init__(self, mdb, apikey ):
        '''
        Constructor
        '''
        super( UpcomingEvents, self ).__init__( apikey, Audit( mdb ), mdb.upcomingEventsCollection())