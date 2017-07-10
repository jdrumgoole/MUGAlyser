'''
Created on 30 Jun 2017

Class of generator functions use to reshape docs as they pass through a processing
pipeline.

@author: jdrumgoole
'''
import datetime
import pprint


def epochToDatetime( ts ):
    return datetime.datetime.fromtimestamp( ts /1000 )

class Reshaper( object ):
    
    def __init_(self, doc ):
        self._doc = doc 
        
    def reshape(self):
        return self._doc
    
    def reshape_one_field(self, d, field_name ):
        self._doc[ field_name] = self._doc[ field_name ]
        return self._doc

    def map_fields( self, d, to_field, from_fields ):
        pass

    def reshape_many_fields(self, d, field_names ):

        for i in field_names:
            self.reshape_one_field( self._doc, i)
        return self._doc
       
    @staticmethod  
    def reshape_time_doc( doc, field_name ): 
        if isinstance( field_name, str ):
            if doc.has_key( field_name ):
                doc[ field_name ] = epochToDatetime( doc[ field_name ])
        return doc   
    
    def reshape_time(self, field_name ):
        self._doc = Reshaper.reshape_time_doc( self._doc, field_name )
        return self._doc
    
    @staticmethod
    def reshape_geospatial_doc( doc,to_field=None, from_fields=None ):
        # long lat format
        
        if to_field is None:
            to_field = "location"
            
        if from_fields is None:
            lon ="lon"
            lat = "lat"
        else:
            ( lon, lat ) = from_fields
            
        if not lon in doc :
            raise ValueError( "No '%s' field in doc" % lon )
        
        if not lat in doc :
            raise ValueError( "No '%s' field in doc" % lat )
        doc[ to_field ] = { "type" : "Point", "coordinates": [ doc[ lon ], doc[ lat ]] }
        del doc[ lon ]
        del doc[ lat ]
        return doc

    def reshape_geospatial( self, to_field=None, from_fields=None ):
        self._doc = self.reshape_geospatial_doc( self._doc, to_field, from_fields)
        return self._doc
   
    def iterate_one_field( self, generator, field_name ) :
        for i in generator:
            yield self.reshape_one_field( i, field_name )
            
    def iterate_many_fields( self, generator, field_names ) :
        for i in generator:
            yield self.reshape_many_fields( i, field_names )
            
    def iterate_map_fields( self, generator, to_field, from_fields ) :
        for i in generator:
            yield self.map_fields( i, to_field, from_fields )


class Reshape_Member( Reshaper ):
    
    time_fields = [ "joined", "join_time", "last_access_time" ]
    
    def __init__(self, doc ):
        self._doc = doc 
        
    def reshape(self ):
        for i in self.time_fields:
            self.reshape_time( i )
            
        return self.reshape_geospatial()

    
class Reshape_Event( Reshaper ):
    
    time_fields = [ "created", "updated", "time" ]
    
    def __init__(self, doc ):
        self._doc = doc 
        
    def reshape(self):
        for i in self.time_fields:
            self.reshape_time( i )
            
        self._doc[ "group" ] = self.reshape_geospatial_doc( self._doc[ "group"], 
                                                            "location",
                                                            [ "group_lon", "group_lat"] )
            
        if self._doc.has_key( "venue"):
            self._doc[ "venue" ] = self.reshape_geospatial_doc( self._doc[ "venue"], 
                                                                "location",
                                                                [ "lon", "lat"] )
        return self._doc
    

class Reshape_Group( Reshaper ):
    
    time_fields = [ "created"  ]

    def __init__(self, doc ):
        self._doc = doc 
        
    def reshape(self):
        for i in self.time_fields :
            self.reshape_time( i )
    
        return self.reshape_geospatial()
    
class Reshape_Pro_Group( Reshaper ):
    
    time_fields = [ "created", "pro_join_date", "founded_date", "last_event" ]

    def __init__(self, doc ):
        self._doc = doc 
        
    def reshape(self):
        for i in self.time_fields :
            self.reshape_time( i )
    
        return self.reshape_geospatial()
# 
# def reshapeMemberDocs( doc_gen ):
#     return ReshapeTime().iterate_many_fields( ReshapeGeospatial().iterate_map_fields(doc_gen, "location",  [ "lon", "lat"]), 
#                                               [ "joined", "join_time", "last_access_time" ])
# 
#     
# def reshapeEventDocs( doc_gen ):
#     return ReshapeTime().iterate_many_fields( doc_gen, [ "created", "updated", "time" ])
#     
#     
# def reshapeGroupDocs( doc_gen ):
#     return ReshapeTime().iterate_many_fields( ReshapeGeospatial().iterate_map_fields(doc_gen, "location",  [ "lon", "lat"]), 
#                                               [ "created", "pro_join_date", "founded_date", "last_event" ])