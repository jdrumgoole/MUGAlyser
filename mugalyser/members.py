'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

from agg import Agg
from mugalyser import MUGAlyser
from requests import HTTPError
from audit import Audit
import logging
from mugs import MUGS
from feedback import Feedback
from batchwriter import BatchWriter

class Members(object):
    '''
    classdocs
    '''
    
    def __init__(self, mdb, apikey ):
        '''
        Constructor
        '''
        self._members = mdb.membersCollection()
        self._audit = Audit( mdb )
        self._mlyser = MUGAlyser( apikey )
        self._membersAgg = Agg( self._members )
        self._membersAgg.addMatch({ "member.name": { "$exists" : 1 }})
        self._membersAgg.addProject( { "_id" : 0, "name" : "$member.name" })
        self._membersAgg.addGroup( { "_id" : "$name" , "occurences" : { "$sum" : 1 }})
        self._membersAgg.addSort( { "occurences" : -1 }) # largest first
        self._memberCount = 0
        self._feedback = Feedback()
        
    def collection( self ):
        return self._members
        
    def get_members(self, url_name ):
        
        memberCount = 0
        try:
            
            self._feedback.output( "Get members for: %s" % url_name )
            membersGenerator = self._mlyser.get_members( url_name, items=200 )
            
            writer = BatchWriter( self._members )
            writer.bulkWrite( membersGenerator, self._audit.addMemberTimestamp )
            return memberCount
        
        except HTTPError, e :
            logging.error( "Stopped members request: %s : %s", url_name, e )
            raise
        
    def get_all_members(self, groups=None):
        
        if groups is None:
            groups = MUGS
        
        for i in groups:
            self._memberCount = self._memberCount + self.get_members( i )
            
        return self._memberCount
        
    def get_by_name(self, name ):
        val = self._members.find_one( { "member.name" : name, "batchID" : self._audit.getCurrentBatchID() })
        
        if val is None:
            return val
        else:
            return val[ "member"]
        
    def get_by_ID(self, member_id):
        val = self._members.find_one( { "member.id" : member_id, "batchID" : self._audit.getCurrentBatchID() })
        
        if val is None:
            return val
        else:
            return val[ "member"]
        
    def bruteCount(self ):
        count = 0
        members = self._members.find({ "member.name": { "$exists" : 1 }}, { "_id" : 0, "member.name" : 1 }).sort( "member.name", 1 )
        seenName = None
        
        for i in members:
            name = i[ "member"]["name"]
            if seenName == name:
                continue
            else:
                count = count + 1 
                seenName = name
 
        return count
    
    def getMembers(self):
        members = self._membersAgg.aggregate()
        for i in members:
            yield i
            
    
        