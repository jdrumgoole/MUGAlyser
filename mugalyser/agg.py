'''

@author: jdrumgoole
'''
import pprint
from datetime import datetime
from collections import OrderedDict
import collections

import pymongo
import csv
import contextlib
import sys

class Sorter( object ):
    '''
    Required for ordered sorting of fields as python dictionaries do not 
    guarantee to maintain insertion order
    '''
    
    def __init__(self,  **kwargs ):
        '''
        parameters are key="asending" or key="descending"
        '''
        self._sorted = {}
        self._sorted[ "$sort"] = OrderedDict()

        self.add( kwargs )
        
    def add(self, sorts ):
        for  k,v in sorts.iteritems():
            self.add_sort( k, v )
            
    def sort_fields(self):
        return self._sorted[ "$sort"].keys()
    
    def sort_items(self):
        return self._sorted[ "$sort"].items()
    
    def sort_directions(self):
        return self._sorted[ "$sort"].values()
    
    def sorts(self):
        return self._sorted
            
    def add_sort(self, field, sortOrder = pymongo.ASCENDING ):
        if sortOrder in [ pymongo.ASCENDING, pymongo.DESCENDING ]:
            self._sorted[ "$sort" ][ field ] = sortOrder
        else:
            raise ValueError( "Invalid sort order must be pymongo.ASCENDING or pymongo.DESCENDING")
    
    def __call__(self):
        return self._sorted
        
    def __str__(self):
        return str( self._sorted )
    
    def __repr__(self):
        return self.__str__()
    
    
class AggFormatter( object ):
    '''
    Take a mongodb Agg object and call aggregate on it.
    IF root is "-" send the output to stdout.
    
    If root is a file name output the content to that file.
    '''
        
    def __init__(self, agg, prefix="", name="-", ext="", results=[] ):
        '''
        Data from cursor
        output to <filename>suffix.ext.
        '''
        self._agg = agg
        self._name = name
        self._prefix = prefix
        self._ext = ext
        self._filename = self._make_filename(prefix, name, ext)
        self._results = results
        
    def results(self):
        return self._results 
    
    @contextlib.contextmanager
    def _smart_open(self, filename=None):
        if filename and filename != '-':
            fh = open(filename, 'wb' )
        else: 
            fh = sys.stdout
    
        try:
            yield fh
        finally:
            if fh is not sys.stdout:
                fh.close()
                
    def _make_filename( self, prefix="", name="-", ext="" ):
        '''
        If root is '-" then we just return that. Otherwise
        we construct a filename of the form:
        <root><suffix>.<ext>
        '''
        
        if name == "-"  or name is None:
            return "-"
        else: 
            return prefix + name + "." + ext


    @staticmethod
    def get_value( d, k ):
        keys = k.split( ".", 1 )
        
        #print( "get_value %s" % k  )
        if len( keys ) == 1 :
            #print( "len(keys) : 1")
            return d[ keys[ 0 ]]
        else:
            #for k,v in dict.__iteritems__( self ):
            #print( "len(keys) : > 1")
            nested = d[ keys[ 0 ]]
            if isinstance( nested, dict ) :
                    return AggFormatter.get_value( nested, keys[ 1 ] )
                    
    @staticmethod
    def set_value( d, k, v ):
        
        keys = k.split( ".", 1 )
        
        if len( keys ) == 1 :
            d[ keys[ 0 ]] = v
        else:
            AggFormatter.set_value( d[ keys[0]], keys[ 1 ], v )
    
    @staticmethod
    def dateMapField( doc, field ):
        
        value = AggFormatter.get_value( doc, field )
        AggFormatter.set_value( doc, field, value.strftime( "%d-%b-%Y" ) )

        return doc
            
    @staticmethod
    def dateMapper( doc, datemap ):
        '''
        For all the fields in "datemap" find that key in doc and map the datetime object to 
        a strftime string.
        '''
        if datemap:
            for i in datemap :
                AggFormatter.dateMapField( doc, i )
        return doc
                
    def printCSVCursor( self, c, fieldnames, datemap ):
        '''
        Output CSV format. items are separated by commas.
        '''
            
        filename = self._make_filename( self._prefix, self._name, self._ext)
        if filename !="-" :
            print( "Writing CSV File: '%s'" % filename )
            
        with self._smart_open( filename ) as output :
            writer = csv.DictWriter( output, fieldnames = fieldnames)
            writer.writeheader()
            count = 0
            for i in c:
                self._results.append( i )
                count = count + 1
                d = AggFormatter.dateMapper( i , datemap)
                x={}
                for k,v in d.items():

                    if type( v ) is unicode :
                        x[ k ] = v
                    else:
                        x[ k ] = str( v ).encode( 'utf8')
                    
                writer.writerow( {k:v.encode('utf8') for k,v in x.items()} ) 
                            
            print( "Total records: %i\n" % count )
            
        return filename

    
    def printJSONCursor( self, c, datemap ):
        '''
        Output plain JSON objects.
        '''
        
        count = 0 
        filename = self._make_filename( self._prefix, self._name, self._ext)
        if filename !="-" :
            print( "Writing JSON file: '%s'" % filename )
        with self._smart_open( filename ) as output:
            for i in c :
                self._results.append( i )
                pprint.pprint( AggFormatter.dateMapper( i, datemap ), output )
                count = count + 1
            print( "Total records: %i\n" % count )

        return filename

    def printCursor( self, c, fieldnames=None, datemap=None  ):
        '''
        Output a cursor to a filename or stdout if filename is "-".
        fmt defines whether we output CSV or JSON.
        '''
    
        if self._ext == 'csv' :
            filename = self.printCSVCursor( c, fieldnames, datemap )
        else:
            filename = self.printJSONCursor( c,  datemap )
            
        return filename
    
    def output(self, fieldNames, datemap=None  ):
        '''
        Output all fields using the fieldNames list. for fields in the list datemap indicates the field must
        be date
        '''

        return self.printCursor( self._agg.aggregate(), fieldNames, datemap )
        
class Agg(object):
    '''
    A wrapper class for the MongoDB Aggregation framework (MongoDB 3.2)
    '''

    def __init__(self, collection ):
        '''
        Constructor
        '''
        self._collection   = collection
        self._hasDollarOut = False
        self._cursor       = None
        self._elapsed      = None
        self.clear()
    
    @staticmethod
    def limit( size ):
        return  { "$limit" : size }
    
    @staticmethod
    def sample( sampleSize ):
        return { "$sample" : { "$size" : sampleSize }}
        
    @staticmethod
    def match( matcher ):
        Agg._typeCheckDict( matcher )
        return { "$match" : matcher  }
     
    @staticmethod
    def project( projector ):
        Agg._typeCheckDict( projector )
        return { "$project" : projector }
    
     
    @staticmethod
    def group( grouper ):
        Agg._typeCheckDict( grouper )
        return { "$group" : grouper }
    
    @staticmethod
    def unwind( unwinder ):
        #Agg._typeCheckDict( unwinder )
        return { "$unwind" : unwinder }
    
    @staticmethod
    def sort( sorter ):
        # we typecheck higher up the stack
        return { "$sort" : sorter }
    
    @staticmethod
    def out( output ):
        return { "$out" : output }
    
    @staticmethod
    def _typeCheckDict( val ):
        if not isinstance( val, dict ):
            t = type( val )
            raise ValueError( "Parameters must be dict objects: %s is a %s object " % ( val, t ))
        

    def _hasDollarOutCheck( self, op ):
        if self._hasDollarOut :
            raise ValueError( "Cannot have more aggregation pipeline operations after $out: operation '%s'" % op )
        
    def addLimit(self, size=None):
        
        if size is None :
            return self
        
        self._hasDollarOutCheck( "limit: %i" % size )
        self._agg.append( Agg.limit( size ))
        
        return self
    
    def addSample(self, size=100):
        
        self._hasDollarOutCheck( "sample: %i" % size )
        self._agg.append( Agg.sample( size ))
        
        return self
    
    def addMatch(self, matcher ):

        self._hasDollarOutCheck( "match: %s" % matcher )
        self._agg.append( Agg.match( matcher ))
        
        return self
        
    def addProject(self, projector ):
        
        self._hasDollarOutCheck( "project: %s" % projector )
        self._agg.append( Agg.project( projector ))
        
        return self

    def addGroup(self, grouper ):
        
        self._hasDollarOutCheck( "group: %s" % grouper )
        self._agg.append( Agg.group( grouper ))
        
        return self
    
    def addSort(self, sorter ):
        '''
        Sorter can be a single dict or a list of dicts.
        '''
        
        self._hasDollarOutCheck( "$sort: %s" % sorter )
        
        if type( sorter) is Sorter:
            self._agg.append( sorter())
        else:
            raise ValueError( "Parameter to addSort must of of type Sorter (type is '%s'" % type( sorter ))
        return self

    def addUnwind(self, unwinder ):
        
        self._hasDollarOutCheck( "`$unwind: %s" % unwinder )
        self._agg.append( Agg.unwind( unwinder ))
        
        return self
    
    def addOut(self, output=None ):
        
        if output is None :
            return self
        
        if self._hasDollarOut :
            raise ValueError( "Aggregation already has $out defined: %s" % self._agg )
        else:
            self._agg.append( Agg.out( output ))
            self._hasDollarOut = True
            
        return self
    
    def clear(self):
        self._agg = []
        self._hasDollarOut = False
        self._elapsed = 0
        self._cursor = None
        
            
        return self
    
    def echo(self):
        pprint.pprint( self._agg )
        print( "" )
        return self
    
    def __str__(self):
        return pprint.pformat( self.__repr__())
    
    def addRangeMatch( self, date_field, start=None, end=None ):
    
        query = None
        if start and end :
            query = { date_field : { "$gte" : start, "$lte" : end }}
        elif start :
            query = { date_field : { "$gte" : start  }}
        elif end :
            query ={ date_field : { "$lte" : end  }}
        
        if query:
            self.addMatch( query )
            
        return self
    
    @staticmethod
    def cond( boolean_expr, thenClause, elseClause ):  #$cond: { if: { $gte: [ "$qty", 250 ] }, then: 30, else: 20 }
        return { "$cond" : { "if" : boolean_expr, "then" : thenClause, "else" :  elseClause }}
    
    def __repr__(self):
        return "%s" % self._agg
    
    def cursor(self):
        return self._cursor 
    
    def elapsed(self):
        return self._elapsed 
    
    def aggregate(self ):
        
        start = datetime.utcnow()
        self._cursor =  self._collection.aggregate( self._agg )
        finish = datetime.utcnow()
        
        self._elapsed = finish - start
        
        return self._cursor
    
    def __call__(self ):
        
        return self.aggregate()
