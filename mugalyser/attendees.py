'''
Created on 1 Nov 2016

@author: jdrumgoole
'''


from mugalyser import MUGAlyser
from requests import HTTPError
from audit import Audit
import logging
from mugs import MUGS
from feedback import Feedback
from batchwriter import BatchWriter

class Attendees(object):
    '''
    
    '''
    def __init__(self, mdb, apikey ):
        '''
        Constructor
        '''
        self._mdb = mdb
        self._attendees = self._mdb.attendeeCollection()
        self._audit = Audit( mdb )
        self._mlyser = MUGAlyser( apikey )
        self._groupCount = 0
        self._feedback = Feedback()
        self._attendeeCount = 0     
        
    def mergeEvents( self, writer ):
        for attendee, event in writer:
            doc = { "attendee" : attendee,
                    "event" : event }
            yield doc 
            
    def get_attendees(self, url_name ):
        
        attendeeCount = 0
        try:
            
            self._feedback.output( "Get attendees for: %s" % url_name )
            attendeesGenerator = self._mlyser.get_attendees( url_name, items=200 )
            
            newWriter = self.mergeEvents( attendeesGenerator )
            
            writer = BatchWriter( self._attendees )
            
            attendeeCount = writer.bulkWrite( newWriter, self._audit.addAttendeeTimestamp )
            return attendeeCount
        
        except HTTPError, e :
            logging.error( "Stopped attendee request: %s : %s", url_name, e )
            raise
        
    def get_all_attendees(self, groups=None):
        
        if groups is None:
            groups = MUGS
        
        for i in groups:
            self._attendeeCount = self._attendeeCount + self.get_attendees( i )
            
        return self._attendeeCount
