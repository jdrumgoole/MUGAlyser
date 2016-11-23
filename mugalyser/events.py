'''
Created on 31 Oct 2016

@author: jdrumgoole
'''

from audit import Audit
from feedback import Feedback
from pprint import pprint
from mugdata import MUGData
import itertools

class Events(MUGData):
    '''
    classdocs
    '''
    
    def __init__(self, mdb, collection_name  ):
        '''
        Constructor
        '''
        super( Events, self ).__init__( mdb, collection_name ) 
    
    def get_all_group_events(self ):
        
        return self.find()
        
    def get_groups_events(self, groups=None ):
        # Groups should be an iterator
        return itertools.chain( *[ self.find( { "event.group.urlname" : i } ) for i in groups ] )

            
    
    @staticmethod
    def summary( e ):
        return "name: {0}\ngroup: {1}\nrsvp:{2}\ntime: {3}\n".format(  e[ "name"], e[ "group"]["name"], e[ "yes_rsvp_count"], e[ "time" ])

    @staticmethod
    def printEvent( event, format = None ):
        if format == "short" :
            print( event[ 'name' ] )
        elif format == "summary" :
            print( Events.summary( event ))
        else:
            pprint( event )
        
class PastEvents(Events):
    '''
    classdocs
    '''
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        super( PastEvents, self ).__init__( mdb, "past_events")
        
class UpcomingEvents(Events):
    '''
    classdocs
    '''


    def __init__(self, mdb ):
        '''
        Constructor
        '''
        super( UpcomingEvents, self ).__init__( mdb, "upcoming_events")