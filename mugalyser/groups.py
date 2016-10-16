'''
Created on 7 Oct 2016

@author: jdrumgoole
'''
from audit import AuditDB

class Attendees(object):
    
    def __init__(self, mdb ):
    
        self._db = mdb.attendeeCollection()
        audit = AuditDB( mdb )
    
    def update_attendee_info(self):
        '''
        Grab attendee info since last attendee batch was run.
        '''
        
    
    
class Groups(object):
    '''
    classdocs
    '''

    def __init__(self, mdb ):
        '''
        Constructor
        '''
        self._mdb = mdb
        self._groups = self._mdb.database()["groups"]
        
    def update_meetup_info(self):
        '''
        get meetup info based on what we have already.
        '''
        pass
    
    def getGroups(self):
        '''
        Get Groups from MongoDB
        '''
        
        pass
        
    