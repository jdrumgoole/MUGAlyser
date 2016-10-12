'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

from agg import Agg

class Members(object):
    '''
    classdocs
    '''
    
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        self._members = mdb.membersCollection()
        self._membersAgg = Agg( self._members )
        self._membersAgg.addMatch({ "member.name": { "$exists" : 1 }})
        self._membersAgg.addProject( { "_id" : 0, "name" : "$member.name" })
        self._membersAgg.addGroup( { "_id" : "$name" , "occurences" : { "$sum" : 1 }})
        self._membersAgg.addSort( { "occurences" : -1 }) # largest first
        
    def getMember(self, name ):
        return self._members.find_one( { "member.name" : name })[ "member"]
        
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
            
        