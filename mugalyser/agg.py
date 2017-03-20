'''

@author: jdrumgoole
'''
import pprint
from datetime import datetime
from collections import OrderedDict
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
        self._sorted[ "$sort" ][ field ] = sortOrder
    
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
        
    def __init__(self, agg, root="-", suffix=None, ext=None ):
        '''
        Data from cursor
        output to <filename>suffix.ext.
        '''
        self._agg = agg
        self._root = root
        self._suffix = suffix
        self._ext = ext
        self._filename = self._make_filename(root, suffix, ext)
        
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
                
    def _make_filename( self, root, suffix=None, ext=None ):
        '''
        If root is '-" then we just return that. Otherwise
        we construct a filename of the form:
        <root><suffix>.<ext>
        '''
        
        filename = None
        
        if root == "-" :
            return root
        else: 
            if suffix:
                filename = root + suffix
            else:
                filename = root
                
            if ext :
                return filename + "." + ext
            
    def printCSVCursor( self, c, filename, fieldnames ):
        '''
        Output CSV format. items are separated by commas.
        '''
            
        if filename !="-" :
            print( "Writing : '%s'" % filename )
            
        with self._smart_open( filename ) as output :
            writer = csv.DictWriter( output, fieldnames = fieldnames)
            writer.writeheader()
            for i in c:
                x={}
                for k,v in i.items():
                    if type( v ) is unicode :
                        x[ k ] = v
                    else:
                        x[ k ] = str( v ).encode( 'utf8')
                    
                writer.writerow( {k:v.encode('utf8') for k,v in x.items()} ) 
    
    
    def printJSONCursor( self, c, filename ):
        '''
        Output plain JSON objects.
        '''
        
        count = 0 
        if filename !="-" :
            print( "Writing : '%s'" % filename )
        with self._smart_open( filename ) as output:
            for i in c :
                pprint.pprint(i, output )
                count = count + 1
            output.write( "Total records: %i\n" % count )


    def printCursor( self, c, filename, fmt, fieldnames=None, datemap=None  ):
        '''
        Output a cursor to a filename or stdout if filename is "-".
        fmt defines whether we output CSV or JSON.
        '''
    
        if fmt == "csv" :
            self.printCSVCursor( c, filename, fieldnames, datemap )
        else:
            self.printJSONCursor( c, filename, datemap )
            
        return filename
    
    def output(self, fieldNames, datemap=None  ):
        '''
        Output all fields using the fieldNames list. for fields in the list datemap indicates the field must
        be date
        '''

        self.printCursor( self._agg.aggregate(), self._filename, self._ext, fieldNames, datemap )
        
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
    
    def addRangeMatch( self, date_field, lower=None, upper=None ):
    
        query = None
        if lower and upper :
            query = { date_field : { "$gte" : lower, "$lte" : upper }}
        elif lower :
            query = { date_field : { "$gte" : lower  }}
        elif upper :
            query ={ date_field : { "$lte" : upper  }}
        
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
