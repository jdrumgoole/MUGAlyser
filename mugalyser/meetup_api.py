'''
Created on 6 Sep 2016

@author: jdrumgoole
'''

import logging
import datetime

from copy import deepcopy

from mugalyser.version import __programName__
from mugalyser.meetup_request import MeetupRequest
from mugalyser.reshape import Reshape_Event, Reshape_Group, Reshape_Member

def makeRequestURL( *args ):
    url = "https://api.meetup.com"
    
    for i in args:
        url = url + "/" + i
        
    return url
# 
# def epochToDatetime( ts ):
#     return datetime.datetime.fromtimestamp( ts /1000 )

# class Reshaper( object ):
#     
#     def reshape_one_field(self, d, field_name ):
#         d[ "field_name"] = d["field_name"]
#         return d
#     
#     def map_fields( self, d, to_field, from_fields ):
#         pass
#     
#     def reshape_many_fields(self, d, field_names ):
# 
#         for i in field_names:
#             self.reshape_one_field( d, i)
#         return d
#             
#     def iterate_one_field( self, generator, field_name ) :
#         for i in generator:
#             yield self.reshape_one_field( i, field_name )
#             
#     def iterate_many_fields( self, generator, field_names ) :
#         for i in generator:
#             yield self.reshape_many_fields( i, field_names )
#             
#     def iterate_map_fields( self, generator, to_field, from_fields ) :
#         for i in generator:
#             yield self.map_fields( i, to_field, from_fields )
#                 
# class ReshapeTime( Reshaper ):
# 
#     def reshape_one_field(self, d, field_name ):
#         if d.has_key( field_name ):
#             d[ field_name ] = epochToDatetime( d[ field_name ])
#         return d
# 
#     
# class ReshapeGeospatial( Reshaper ) :
# 
#     def map_fields( self, d, to_field, from_fields ):
#         # long lat format
#         
#         ( lon, lat ) = from_fields
#         d[ to_field ] = { "type" : "Point", "coordinates": [ d[ lon ], d[ lat ]] }
#         del d[ lon ]
#         del d[ lat ]
#         return d
# 
# def reshapeMemberDoc( d ):
#     return ReshapeTime().iterate_many_fields( ReshapeGeospatial().iterate_map_fields(d, "location",  [ "lon", "lat"]), 
#                                               [ "joined", "join_time", "last_access_time" ])
# 
#     
# def reshapeEventDoc( d ):
#     return ReshapeTime().iterate_many_fields( d, [ "created", "updated", "time" ])
#     
#     
# def reshapeGroupDoc( doc_generator ):
#     rs = ReshapeTime()
#     rg = ReshapeGeospatial()
#     
#     for i in doc_generator:
#         doc = rg.map_fields( i, "location",  [ "lon", "lat"] )
#         doc = rs.reshape_many_fields( doc, [ "created", "pro_join_date", "founded_date", "last_event" ] )
#         yield doc

        
    
# def getHeaderLink( header ):
#     #print( "getHeaderLink( %s)" % header )
# 
#     if "," in header:
#         ( nxt, _ ) = header.split( ",", 2 )
#     else:
#         nxt = header
#         
#     ( link, relParam ) = nxt.split( ";", 2 )
#     ( _, relVal ) = relParam.split( "=", 2 )
#     link = link[1:-1] # strip angle brackets off link
#     relVal = relVal[ 1:-1] # strip off quotes
#     return ( link, relVal )


        
class MeetupAPI(object):
    '''
    classdocs
    '''

    
    def __init__(self, apikey, page=200, reshape=None):
        '''
        Constructor
        '''
        
        self._logger = logging.getLogger( __programName__)
        self._api = "https://api.meetup.com/"
        self._params = {}
        self._params[ "key" ] = apikey
        self._params[ "page" ] = page
        self._reshape = reshape
        self._requester = MeetupRequest()
    
            
    def get_group(self, url_name ):
        
        ( _, group ) = self._requester.simple_request( self._api + url_name, params = self._params )
        
        if self._reshape:
            return Reshape_Group( group ).reshape()
        else:
            return group

    def get_groups_by_url(self, urls ):
        for i in urls:
            yield self.get_group( i )
            

        
    def get_all_attendees(self, groups=None ):
        groupsIterator = None
        if groups :
            groupsIterator = groups
        else:
            groupsIterator = self.get_groups()
            
        for group in groupsIterator :
            return self.get_attendees(group )
        
    def get_attendees( self, url_name ):
        
        for event in self.get_past_events( url_name ):
            #pprint( event )
            for attendee in self.get_event_attendees(event[ "id"], url_name ):
                yield ( attendee, event )
    
            
    def get_event_attendees(self, eventID, url_name ):
        
        #https://api.meetup.com/DublinMUG/events/62760772/attendance?&sign=true&photo-host=public&page=20
        reqURL = makeRequestURL( url_name, "events", str( eventID ), "attendance")
        return self._requester.paged_request( reqURL, self._params )
    
    def get_upcoming_events(self, url_name ):
        
        params = deepcopy( self._params )
        params[ "status" ] = "upcoming"
        params[ "group_urlname"] = url_name
        
        return self._requester.paged_request( self._api + "2/events", params )
    
    def get_past_events(self, url_name ) :
        
        params = deepcopy( self._params )
        
        params[ "status" ]       = "past"
        params[ "group_urlname"] = url_name
        
        if self._reshape:
            return ( Reshape_Event( i ).reshape() for i in self._requester.paged_request( self._api + "2/events", params ))
        else:
            return self._requester.paged_request( self._api + "2/events", params )
    def get_member_by_id(self, member_id ):

        ( _, body ) = self._requester.simple_request( self._api + "2/member/" + str( member_id ), params = self._params )
        
        if self._reshape:
            return Reshape_Member( body ).reshape()
        else:
            return body
    
    def get_members(self , urls ):
        for i in urls:
            for member in self.__get_members( i ):
                yield member
                
    def __get_members(self, url_name ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
 
        if self._reshape:
            return ( Reshape_Member( i ).reshape() for i in self._requester.paged_request( self._api + "2/members", params ))
        else:
            return self._requester.paged_request( self._api + "2/members", params )
    
    def get_groups(self ):
        '''
        Get all groups associated with this API key.
        '''
        self._logger.debug( "get_groups")
        
        if self._reshape :
            return ( Reshape_Group( i ).reshape() for i in self._requester.paged_request(self._api + "self/groups",  self._params ))
        else:
            return self._requester.paged_request(self._api + "self/groups",  self._params )
        
    def get_pro_groups(self  ):
        '''
        Get all groups associated with this API key.
        '''
        self._logger.debug( "get_pro_groups")
        
        if self._reshape:
            return ( Reshape_Group( i ).reshape() for i in self._requester.paged_request( self._api + "pro/MongoDB/groups", self._params ))
        else:
            return self._requester.paged_request( self._api + "pro/MongoDB/groups", self._params )
        
    def get_pro_group_names( self ):
        for i in self.get_pro_groups() :
            yield i[ "urlname" ]
            
    def get_pro_members(self ):
        
        self._logger.debug( "get_pro_members")
        #print( self._params )
        
        if self._reshape:
            return ( Reshape_Member( i ).reshape() for i in self._requester.paged_request( self._api + "pro/MongoDB/members", self._params ))
        else:
            return self._requester.paged_request( self._api + "pro/MongoDB/members", self._params )
    