'''
Created on 1 Nov 2016

@author: jdrumgoole
'''

from .mugdata import MUGData
        
class Attendees( MUGData ):
    
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        super( Attendees, self ).__init__( mdb, "attendees")   
    
    def get_attendees(self, event_url):
        
        attendees = self.find( { "info.event.event_url" : event_url })
        for i in attendees :
            yield i

        
    def get_all_attendees(self ):
        
        attendees = self.find()
        for i in attendees:
            yield i
