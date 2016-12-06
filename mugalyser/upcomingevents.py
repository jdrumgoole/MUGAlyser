'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

from .audit import Audit

class UpcomingEventsx(object):
    '''
    classdocs
    '''
    
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        self._mdb = mdb 
        self._events= mdb.upcomingEventsCollection()
        self._audit = Audit( mdb )
        
    def upcoming( self ):
        
        batchID = self._audit.getCurrentBatchID()
        #print( "Current Batch ID: %s" % lastBatchID )
        return self._events.find( { "batchID" : batchID})
            
    def summary(self, e ):
        
        return "name: {0}\ngroup: {1}\nrsvp:{2}\ntime: {3}\n".format(  e[ "name"], e[ "group"]["name"], e[ "yes_rsvp_count"], e[ "time" ])
    
        #return "name: '%s' group: '%s' rsvp: %s time: %s" % ( e[ "name"], e[ "group"]["name"], e[ "yes_rsvp_count"], e[ "time" ] )
    
    