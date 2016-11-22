'''
Created on 31 Oct 2016

@author: jdrumgoole
'''

from audit import Audit
import logging
from mugs import MUGS
from feedback import Feedback
from pprint import pprint


class Events(object):
    '''
    classdocs
    '''
    
    def __init__(self, auditor, eventCollection ):
        '''
        Constructor
        '''
        self._events = eventCollection
        self._audit = auditor
        self._eventCount = 0
        self._feedback = Feedback()
    
    def get_group_events(self, url_name ):
        
        validBatchID = self._audit.getValidBatchID()
        #print( "Current Batch ID: %s" % validBatchID )
        events = self._events.find( { "batchID" : validBatchID})
            
        for i in events:
            yield i 
        
    def get_groups_events(self, groups=None ):
        
        if groups is None:
            groups = MUGS
            
        for i in groups:
            yield self._get_events( i )
            
    
    @staticmethod
    def summary( e ):
        return "name: {0}\ngroup: {1}\nrsvp:{2}\ntime: {3}\n".format(  e[ "name"], e[ "group"]["name"], e[ "yes_rsvp_count"], e[ "time" ])

    @staticmethod
    def printEvent( event, summary = False ):
        if format == "short" :
            print( event[ 'name'] )
        elif format == "summary" :
            print( Events.summary( event ))
        else:
            pprint( event )
        
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