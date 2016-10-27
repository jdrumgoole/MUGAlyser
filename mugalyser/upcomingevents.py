'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

from agg import Agg

from audit import AuditDB

class UpcomingEvents(object):
    '''
    classdocs
    '''
    
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        self._mdb = mdb 
        self._events= mdb.upcomingEventsCollection()
        self._audit = AuditDB( mdb )
        
    def upcoming( self ):
        
        currentBatchID = self._audit.getCurrentBatchID()
        
        events = self._events.find( { "batchID" : currentBatchID})
            
        for i in events:
            yield i 
            
    def summary(self, e ):
        return "name: '%s' rsvp: %s time: %s" % ( e[ "name"], e[ "yes_rsvp_count"], e[ "time" ] )