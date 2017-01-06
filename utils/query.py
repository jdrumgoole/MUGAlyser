'''
Created on 7 Dec 2016

@author: jdrumgoole
'''
def to_minutes( milliseconds ):
    return milliseconds / 1000 /60

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
    
    def __str__(self ):
        return self.__repr__() 
    
    def __call__(self):
        return self.__repr__()
    
    def __repr_(self):
        return self._query
    
    def update(self, q ):
        self._query.update( q._query )
        return self
    
    def And(self, q2 ):
        
        self._query = { "$and" : [ self._query, q2 ]}
        
        return self