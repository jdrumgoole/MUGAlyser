'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

from mugalyser.agg import Agg, Sorter
from mugalyser.feedback import Feedback
from mugalyser.mugdata import MUGData
import itertools
import pymongo

from mugalyser.audit import Audit
from utils.query import Query

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
        self._membersAgg.addSort( Sorter( occurences = pymongo.DESCENDING  )) # largest first
        self._memberCount = 0
        self._feedback = Feedback()
        self._audit = Audit( mdb )
        
    def get_group_members(self, url_name, q=None ):
        '''
        returns a MongoDB cursor.
        '''
        query = { "member.chapters" : { "$elemMatch" : { "urlname" : url_name }}}
        if q :
            query.update( q )

        return self.find( query )
        
    def get_many_group_members(self, groups, query=None):
        '''
        returns a generator
        '''
        
        return itertools.chain( *[ self.get_group_members( i, query ) for i in groups ] )

    def count_members(self, groups ):
        
        total = 0 
        for i in groups:
            count = self.get_group_members( i ).count()
            total = total + count
            
        return count
    
    def get_all_members(self, query=None ):
        '''
        Query meetup API for multiple groups.
        '''
        return self.find( query )
        
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
        
    def get_by_join_date(self, start, end ):

        return self.find( { "member.join_time" : { "$gte" : start, "$lte" : end  }})
        
    def joined_by_year(self):
        
        agg_pipe = Agg( self._collection )    
        agg_pipe.addMatch( { "batchID" : self._audit.getCurrentBatchID() } )
        agg_pipe.addProject( { "_id" : 0, 
                               "member_id" : "$member.member_id",
                               "member_name" : "$member.member_name",
                               "year" : { "$year" : "$member.join_time" },
                              })
        agg_pipe.addGroup( { "_id" : "$year","total_registered" : { "$sum" : 1 }})
        
        return agg_pipe.aggregate()
        
        
    def get_members(self):
        return self._membersAgg.aggregate()
      
    def summary(self, doc ):
        return "name: %s, id: %s, country: %s" % ( doc[ "member" ][ "member_name"],
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
            