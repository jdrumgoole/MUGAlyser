'''
Created on 4 Apr 2017

@author: jdrumgoole
'''
    
class Nested_Dict( object ):
    '''
    Allow dotted access of nested dicts.
    so :
    a[ "x.y.z" ] = 1 is equivalent to a[ x[ y[ z ]]] = 1
    
    a = { x : { y : z }}}
    '''
    
    def __init__(self, d={}):
        
        if isinstance( d, dict ):
            self._dict = d
        else:
            raise ValueError( "d is not a dict type")

    def dict_value(self ):
        return self._dict
    
    def get_value( self, k ):
        keys = k.split( ".", 1 )
        
        #print( "get_value %s" % k  )
        if len( keys ) == 1 :
            #print( "len(keys) : 1")
            return self._dict[ keys[ 0 ]]
        elif self._dict.has_key( keys[ 0 ]) :
                nested = self._dict[ keys[ 0 ]]
        else:
            raise ValueError( "nested key :'%s' does not exist in keys %s of %s" % ( keys[ 0 ], keys, self._dict ))
        
        if isinstance( nested, dict ) :
            nested = Nested_Dict( nested )
            return nested.get_value( keys[ 1 ] )
        else:
            return nested
    
    def has_key( self, k ):
        
        keys = k.split( ".", 1 )
        nested = None
        if len( keys ) == 1 :
            return self._dict.has_key( keys[ 0 ] )
        elif self._dict.has_key( keys[ 0 ]) :
                nested = self._dict[ keys[ 0 ]]
        else:
            raise ValueError( "nested key :'%s' does not exist" % keys[ 0 ])
        
        if isinstance( nested, dict ) :
            nested = Nested_Dict( nested )
            return nested.has_key( keys[ 1 ] )
        else:
            return True
                      
        
    def set_value( self, k, v ):
        
        keys = k.split( ".", 1 )
        nested = None
        if len( keys ) == 1 :
            self._dict[ keys[ 0 ]] = v
            return self
        elif self._dict.has_key( keys[ 0 ]) :
            nested = self._dict[ keys[ 0 ]]
        else:
            self._dict[ keys[ 0 ]] = {}
            nested = self._dict[ keys[ 0 ]]
        
        if isinstance( nested, dict ) :
            nested = Nested_Dict( nested )
            nested.set_value( keys[ 1 ], v )
            return self



class dotted_dict( dict ):
    '''
    Allow dotted access of nested dicts.
    so :
    a[ "x.y.z" ] = 1 is equivalent to a[ x[ y[ z ]]] = 1
    
    a = { x : { y : z }}}
    '''
    def __init__( self, *args, **kwargs ):
        super( dotted_dict, self).__init__( *args, **kwargs )


    def dict_value(self ):
        return self._dict
    
    def get_value( self, k ):
        keys = k.split( ".", 1 )
        
        #print( "get_value %s" % k  )
        if len( keys ) == 1 :
            #print( "len(keys) : 1")
            return self._dict[ keys[ 0 ]]
        elif self._dict.has_key( keys[ 0 ]) :
                nested = self._dict[ keys[ 0 ]]
        else:
            raise ValueError( "nested key :'%s' does not exist in keys %s of %s" % ( keys[ 0 ], keys, self._dict ))
        
        if isinstance( nested, dict ) :
            nested = NestedDict( nested )
            return nested.get_value( keys[ 1 ] )
        else:
            return nested
    
    def has_key( self, k ):
        
        keys = k.split( ".", 1 )
        nested = None
        if len( keys ) == 1 :
            return self._dict.has_key( keys[ 0 ] )
        elif self._dict.has_key( keys[ 0 ]) :
                nested = self._dict[ keys[ 0 ]]
        else:
            raise ValueError( "nested key :'%s' does not exist" % keys[ 0 ])
        
        if isinstance( nested, dict ) :
            nested = NestedDict( nested )
            return nested.has_key( keys[ 1 ] )
        else:
            return True
                      
        
    def set_value( self, k, v ):
        
        keys = k.split( ".", 1 )
        nested = None
        if len( keys ) == 1 :
            self._dict[ keys[ 0 ]] = v
            return self
        elif self._dict.has_key( keys[ 0 ]) :
            nested = self._dict[ keys[ 0 ]]
        else:
            self._dict[ keys[ 0 ]] = {}
            nested = self._dict[ keys[ 0 ]]
        
        if isinstance( nested, dict ) :
            nested = NestedDict( nested )
            nested.set_value( keys[ 1 ], v )
            return self