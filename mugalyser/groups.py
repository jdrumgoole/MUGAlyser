'''
Created on 7 Oct 2016

@author: jdrumgoole
'''

class Groups(object):
    '''
    classdocs
    '''


    def __init__(self, mdb ):
        '''
        Constructor
        '''
        self._groups = mdb.database()["groups"]
        
    def getGroups(self):
        pass
    