'''
Created on 7 Oct 2016

@author: jdrumgoole
'''
from audit import Audit
import logging
from mugs import MUGS
from feedback import Feedback
from pprint import pprint
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
        self._groupCount = 0
        self._feedback = Feedback()
        
    def get_meetup_group(self, url_name ):
    
        batchID = self._audit.getCurrentBatchID()
        return self._groups.find_one( { "batchID" : batchID, "group.urlname" : url_name })
 
    def get_meetup_groups(self, group_names=None ):
        self._groupCount = 0
        
        if group_names is None:
            self._group_names = MUGS
        else:
            self._group_names = group_names
        
        for i in self._group_names:
            yield self.get_meetup_group( i )   

    @staticmethod
    def summary( g ):
        return u"name: {0}\nmembers:{1}\ncountry: {2}\n".format( g[ "name" ], 
                                                                g[ "members" ], 
                                                                g[ "country" ])
    
    
    @staticmethod
    def printGroup( group, format="short" ):
        
        if format == "short" :
            print( group[ 'name' ] )
        elif format == "summary" :
            print( Groups.summary( group ))
        else:
            pprint( group )
        
    