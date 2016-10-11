'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

class Members(object):
    '''
    classdocs
    '''
    
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        self._members = mdb.membersCollection()
        
    def getMember(self, name ):
        return self._members.find_one( { "member.name" : name })[ "member"]
        
    def getMembers(self):
        for i in self._members.distinct( "member.name" ):
            yield i
        