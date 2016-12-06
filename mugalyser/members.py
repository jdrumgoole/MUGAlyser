'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

from agg import Agg
import logging
from feedback import Feedback
from mugdata import MUGData
import itertools

class Members(MUGData):
    '''
    classdocs
    '''
    
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        super( Members, self ).__init__( mdb, "members" ) 
        self._membersAgg = Agg( self._collection )
        self._membersAgg.addMatch({ "member.name": { "$exists" : 1 }})
        self._membersAgg.addProject( { "_id" : 0, "name" : "$member.name" })
        self._membersAgg.addGroup( { "_id" : "$name" , "occurences" : { "$sum" : 1 }})
        self._membersAgg.addSort( { "occurences" : -1 }) # largest first
        self._memberCount = 0
        self._feedback = Feedback()
        
    def get_group_members(self, url_name ):
        '''
        returns a MongoDB cursor.
        '''
        
        return self.find( { "member.chapters" : { "$elemMatch" : { "urlname" : url_name }}})
        
    def get_many_group_members(self, groups ):
        '''
        returns a generator
        '''
        
        return itertools.chain( *[ self.get_group_members( i ) for i in groups ] )

    def get_all_members(self ):
        '''
        Query meetup API for multiple groups.
        '''
        return self.find()
        
    def distinct_members(self ):
        return self._collection.distinct( "member.member_name")
    
    def get_by_name(self, name ):
        member = self.find_one( { "member.member_name" : name })
        
        if member is None:
            return None
        else:
            return member[ "member" ]
        
    def get_by_ID(self, member_id):
        val = self.find_one( { "member.member_id" : member_id })
        
        if val is None:
            return val
        else:
            return val[ "member" ]
        
        
    def bruteCount(self ):
        count = 0
        members = self._collection.find({ "member.name": { "$exists" : 1 }}, { "_id" : 0, "member.name" : 1 }).sort( "member.name", 1 )
        seenName = None
        
        for i in members:
            name = i[ "member"]["name"]
            if seenName == name:
                continue
            else:
                count = count + 1 
                seenName = name
 
        return count
    
    def get_members(self):
        return self._membersAgg.aggregate()
    

            
    def summary(self, doc ):
        return " name: %s, id: %s, country: %s" % ( doc[ "member" ][ "member_name"],
                                                    doc[ "member" ][ "member_id"],
                                                    doc[ "member" ][ "country" ] )
    
    def one_line(self, doc ):
        return "name : %s, id: %s" % ( doc[ "member"][ "member_name"],
                                       doc[ "member" ][ "member_id"] )

    
        
class Organizers( Members ):
    
    def get_organizers(self):
        return self.find( { "member.is_organizer" : True })
    
    def get_mugs(self, organizer_name  ):
        
        doc = self.find_one( { "member.is_organizer" : True, 
                               "member.member_name"  : organizer_name } )
        
        return doc["member"][ "chapters" ]
        
    def summary(self, doc ):
        m = doc[ "member"]
        
        header = " name: %s, id: %s, country: %s\n" % ( m[ "member_name"],
                                                        m[ "member_id"],
                                                        m[ "country" ] )
        
        for i in m[ "chapters" ]  :
            header = "%s \t%s\n" % ( header, i[ "urlname" ] ) 
            
        return header
            