'''
Created on 31 Oct 2016

@author: jdrumgoole
'''

from audit import Audit
from feedback import Feedback
from pprint import pprint
from mugdata import MUGData
import itertools
from utils.query import Query

class Events(MUGData):
    '''
    classdocs
    '''
    
    def __init__(self, mdb, collection_name  ):
        '''
        Constructor
        '''
        super( Events, self ).__init__( mdb, collection_name ) 
    
    def get_all_events(self, query ={}):
        return self.find( query )
    def get_all_group_events(self, groups=[ "all" ] ):
        
        if "all" in groups:
            return self.find()
        else:
            return itertools.chain( *[ self.get_group_events( i )  for i in groups ] )
        
    def get_group_events(self, url_name ):
        return self.find( { "event.group.urlname" : url_name } )
    
#     def get_groups_events(self, groups=[] ):
#         # Groups should be an iterator
#         return itertools.chain( *[ self.get_group_events( i )  for i in groups ] )

    def summary( self, doc ):
        event  = doc[ "event"]
        group  = event[ "group" ]
        return u"name: {0}\ngroup: {1}\nrsvp:{2}\ntime: {3}\n".format(  event[ "name"], 
                                                                        group[ "urlname" ], 
                                                                        event[ "yes_rsvp_count"], 
                                                                        event[ "time" ] )
    
    def one_line(self, doc ):
        event  = doc[ "event"]
        group  = event[ "group" ]
        return u"name: {0}, date: {1}, group: {2}".format(  event[ "name"], 
                                                            event[ "time" ],
                                                            group[ "urlname" ],)

        
class PastEvents(Events):
    '''
    classdocs
    '''
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        super( PastEvents, self ).__init__( mdb, "past_events")
        
    def get_all_group_events(self, groups=[ "all" ] ):
        
        if "all" in groups:
            return self.find({ "event.status" : "past"})
        else:
            return itertools.chain( *[ self.get_group_events( i )  for i in groups ] )
        
    def get_group_events(self, url_name ):
        return self.find( { "event.group.urlname" : url_name,
                            "event.status" : "past" } )
    
class UpcomingEvents(Events):
    '''
    classdocs
    '''


    def __init__(self, mdb ):
        '''
        Constructor
        '''
        super( UpcomingEvents, self ).__init__( mdb, "upcoming_events")
        
    def get_all_group_events(self, groups=[ "all" ] ):
        
        if "all" in groups:
            return self.find( { "event.status" : "ucpoming"})
        else:
            return itertools.chain( *[ self.get_group_events( i )  for i in groups ] )
        
    def get_group_events(self, url_name ):
        return self.find({ "event.group.urlname" : url_name,
                           "event.status"        : "upcoming" } )