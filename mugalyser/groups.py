'''
Created on 7 Oct 2016

@author: jdrumgoole
'''
from audit import Audit
from mugalyser import MUGAlyser
from requests import HTTPError
import logging
from mugs import MUGS
from feedback import Feedback
    
class Groups(object):
    '''
    classdocs
    '''

    def __init__(self, mdb, apikey ):
        '''
        Constructor
        '''
        self._mdb = mdb
        self._groups = self._mdb.groupsCollection()
        self._audit = Audit( mdb )
        self._mlyser = MUGAlyser( apikey )
        self._groupCount = 0
        self._feedback = Feedback()
        
    def get_meetup_group(self, url_name ):
    
        try :
            self._feedback.output( "Processing group: %s" % url_name )
            group = self._mlyser.get_group( url_name )
            self._groups.insert_one( self._audit.addGroupTimestamp( group))
            return group
    
        except HTTPError, e :
            logging.error( "Stopped get_meetup_group request: %s : %s", url_name, e )
            raise
        
    def get_meetup_groups(self, group_names=None ):
        self._groupCount = 0
        
        if group_names is None:
            self._group_names = MUGS
        else:
            self._group_names = group_names
        
        for i in self._group_names:
            self.get_meetup_group( i )
            self._groupCount = self._groupCount + 1 
            
        return self._groupCount
            

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
        
    