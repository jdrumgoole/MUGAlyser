'''
Created on 7 Dec 2016

@author: jdrumgoole
'''

class Query(object):
    '''
    classdocs
    '''

    def __init__(self, query=None ):
        '''
        Constructor
        '''
        if query == None:
            self._query = {}
        else:
            self._query = query
        
    def add(self, field, value ):
        
        self._query.update( { field : value })
        return self
    
    def add_range(self, field, start, finish ):
    
        return self.add( field, { "$gte" : start, "$lte" : finish  })    
        
    def query(self):
        return self._query
    
    def update(self, q ):
        self._query.update( q._query )
        return self