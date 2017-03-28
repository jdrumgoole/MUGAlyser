'''
Created on 21 Mar 2017

@author: jdrumgoole
'''
import datetime

class Nested_Dict( dict ):
    '''
    classdocs
    '''    
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        '''
        Accept a key of the form "a.b.c". We expect the object to have a set of nested dicts
        { a : ....
              b : { ....
                    c: ....
                }
            }
        } 
        
        If a,b and c exist as keys return the value of c.
        If any of the nested keys doesn't exist return value error.
               
        '''
        keys = key.split( ".", 1 )
        
        print( "getitem: %s" % key )
        if len( keys ) == 1 :
            print( "len(keys) : 1")
            print( "self: %s" % self )
            return dict.__getitem__( self, keys[ 0 ])
        else:
            #for k,v in dict.__iteritems__( self ):
            print( "len(keys) : > 1")
            nested = dict.__getitem__(  self, keys[ 0 ] )
            if isinstance( nested, dict ) :
                    return Nested_Dict.__getitem__( Nested_Dict( nested ), keys[ 1 ] )
                    

    def __setitem__(self, key, val):
        
        keys = key.split( ".", 1 )
        
        print( "setitem: %s" % key )
        if len( keys ) == 1 :
            print( "len(keys) : 1")
            print( "self: %s" % self )
            return dict.__setitem__( self, keys[ 0 ], val )
        else:
            #for k,v in dict.__iteritems__( self ):
            print( "len(keys) : > 1")
            if isinstance( dict.__getitem__(  self, keys[ 0 ] ), dict ) :
                    return Nested_Dict.__setitem__( Nested_Dict.__getitem__( self, keys[ 0 ] ), keys[ 1 ], val )

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)
    
    def update(self, *args, **kwargs ):
        print 'update', args, kwargs
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v
        
def get_value( d, k ):
    keys = k.split( ".", 1 )
    
    print( "get_value %s" % k  )
    if len( keys ) == 1 :
        print( "len(keys) : 1")
        return d[ keys[ 0 ]]
    else:
        #for k,v in dict.__iteritems__( self ):
        print( "len(keys) : > 1")
        nested = d[ keys[ 0 ]]
        if isinstance( nested, dict ) :
                return get_value( nested, keys[ 1 ] )
                

def set_value( d, k, v ):
    
    keys = k.split( ".", 1 )
    
    if len( keys ) == 1 :
        d[ keys[ 0 ]] = v
    else:
        set_value( d[ keys[0]], keys[ 1 ], v )
        
if __name__ == "__main__" :
    print( "hello")
    
    nested = { "a" : 
              { "b" : 
               { "c" : datetime.datetime.now() }}}

    d = Nested_Dict(nested )
    
    print( get_value( d,  'a.b.c'))
    print( get_value( d,  'a.b'))
    print( get_value( d,  'a' ))
    
    nested = { "x" : 10,
               "a" : 
              { "b" : 
               { "c" : datetime.datetime.now() }}}
    
    d = Nested_Dict(nested )
    
    print( get_value( d, 'a.b.c'))
    print( get_value( d, 'a.b' ))
    print( get_value( d, 'a' ))
    print( get_value( d, 'x' ))
    
    
    print( set_value( d, 'x', 12 ))
    
    set_value( d,  'a.b.c', "hello" )
    print( d )