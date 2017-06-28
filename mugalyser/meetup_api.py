'''
Created on 6 Sep 2016

@author: jdrumgoole
'''

import requests
import logging
import datetime
import time
import pprint
import json

from copy import deepcopy

from mugalyser.version import __programName__
def returnData( r ):
    #print( r.text )
    if r.raise_for_status() is None:
        return ( r.headers, r.json())
        

class MeetupRequest( object ):
    
    def __init__(self, items ):
        '''
        No of items to return per page for paged requests is specified by items
        '''
        self._items = items
        self._logger = logging.getLogger( __programName__)
        
         
    def simple_request(self, req, params=None ):
        '''
        The meetup_api occasionally returns a message with no body. When it does the Content-Length is either
        0 or not present. When it does we retry
        one time and then give up.
        '''
        
        json_data = {}
        if params :
            r = requests.get( req, params, stream=True )
        else:
            r = requests.get( req, stream=True )
            
        try:
    
            if r.raise_for_status() is None:
    
                for req_data in r.iter_lines():
                    if req_data:
                        print( "req_data")
                        #pprint.pprint( req_data )
                        json_data = json.loads(req_data)
            
            '''
            Rate limiting
            '''
            remaining = int( r.headers[ "X-RateLimit-Remaining"] )
            resetDelay = int( r.headers[ "X-RateLimit-Reset"] )
            if remaining <= 1 and resetDelay > 0 :
                self._logger.debug( "Sleeping for : %i", resetDelay )
                time.sleep( resetDelay )
                
            return ( r.headers, json_data )
        
        except ValueError :
            self._logger.error( "ValueError in makeRequests:")
            self._logger.error( "request: '%s'", r.url)
            self._logger.error( "headers:" )
            self._logger.error( pprint.pformat( r.headers ))
            self._logger.error( "text:" )
            self._logger.error( r.text )
            raise
        
        except requests.HTTPError, e :
            self._logger.error( "HTTP Error  : %s:", e )
            raise

    def getHref( self, s ):
        ( link, direction ) = s.split( ";", 2 )
        link = link[ 1:-1]
        ( _, direction ) = direction.split( "=", 2 )
        direction = direction[ 1:-1 ]
        return ( link, direction )
    
    def getNextPrev(self, header ):
        
        #headerDict = json.loads( header )
        link = header[ "Link" ]
        
        if "," in link : # has prev  and next fields
            ( nxt, prev ) = link.split( ",", 2 )
            ( nextLink, _ ) = self.getHref( nxt )
            ( prevLink, _ )  = self.getHref( prev )
        else:
            ( link, direction ) = self.getHref( link )
            #print( "direction: '%s'" % direction )
            if direction == "next" :
                nextLink = link
                prevLink = None
            else:
                prevLink = link
                nextLink = None
        
        return ( nextLink, prevLink )
    
    def paged_request(self, req, params, reshaperFunc=None ):
        '''
        Takes a request and hands it off to the paginator API. It does this by initiating the request
        to get the first document back and then using it to look for headers.
        '''

        #print( "Intiate paginated request")    
        (header, body) = self.simple_request( req, params )
        
        print( "header" )
        pprint.pprint( header )
        print( "body")
        pprint.pprint( body[ "meta"] )
        #print( "Paginator")
        #r = requests.get( self._api + url_name + "/events", params = params )
        #print( "request: '%s'" % r.url )
        #print( "header: '%s' )
        return self.next_page( header, body, params, func=reshaperFunc  )
    
    def next_page( self, headers, body, params, func=None ):
        '''
        Meetup API returns results as pages. The old API embeds the 
        page data in a meta data object in the response object. The new API
        returns page data in the Header info. 
        
        Func is a function that takes a doc and returns a doc. Right now
        we use this to reshape geospatial coordinates into a format that MongoDB
        understands and to convert  meetup timestamps to datetime objects.
        
        next_page is a generator which yields results.
        
        '''
        #print( "paginator( header= '%s'\n, body='%s'\n, params='%s'\n)" % ( headers, body, params ))
        #print( "paginatorEntry( %s )" % headers )
        if func is None:
            func = Reshaper.noop
            

        #pprint.pprint( data )
        
        # old style format 
        if "meta" in body :
            for i in body[ "results"]:
                yield func( i )
        
            count = 0
            while ( body[ 'meta' ][ "next" ] != ""  ) :

                #print( "makeRequest (old): %i" % count )
                ( _, nested_body ) = self.simple_request( body['meta'][ 'next' ] )[1]
                count = count + 1

                if nested_body:
                    for i in nested_body[ "results"]:
                        yield  func( i )
    
                    
        elif ( "Link" in headers ) : #new style pagination
            for i in body :
                if i:
                    yield func( i )
               
            count = 0 
            ( nxt, _) = self.getNextPrev(headers)

            
            while ( nxt is not None ) : # no next link in last page

                count = count + 1 
                #print( "make request (new): %i" % count )
                    

                ( headers, body ) = self.simple_request( nxt, params )
                ( nxt, _ ) = self.getNextPrev(headers)
                for i in body :
                    yield  func( i )
    
        else: # new style but we have all the data
            for i in body:
                yield func( i )
                
    @staticmethod
    def makeRequestURL( *args ):
        url = "https://api.meetup.com"
        
        for i in args:
            url = url + "/" + i
            
        return url

def epochToDatetime( ts ):
    return datetime.datetime.fromtimestamp( ts /1000 )

class Reshaper( object ):
    
    def __init__(self ):
        self._reshape = {}
        
    def add( self, key, value ):
        self._reshape[ key] = value
        
    @staticmethod
    def noop( d ):
        return d
 
    def reshape( self, doc ) :
        newDoc = doc.copy()
        newDoc.update( self._reshape )
        return newDoc

    @staticmethod
    def reshapeGeospatial( doc ):
        doc[ "location" ] = { "type" : "Point", "coordinates": [ doc["lon"], doc["lat" ]] }
        del doc[ 'lat']
        del doc[ 'lon']
        return doc

    @staticmethod
    def reshapeMemberDoc( doc ):
        return Reshaper.reshapeTime( Reshaper.reshapeGeospatial(doc), [ "joined", "join_time", "last_access_time" ])

    @staticmethod
    def reshapeEventDoc( doc ):
        return Reshaper.reshapeTime( doc, [ "created", "updated", "time" ])
    
    @staticmethod
    def reshapeTime( doc, keys ):
        for i in keys:
            if i in doc :
                doc[ i ] =epochToDatetime( doc[ i ])
        
        return doc
    
    @staticmethod
    def reshapeGroupDoc( doc ):
        return Reshaper.reshapeTime( Reshaper.reshapeGeospatial(doc), 
                                     [ "created", "pro_join_date", "founded_date", "last_event" ])
        
    
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

    
    def __init__(self, apikey, items=500):
        '''
        Constructor
        '''
        
        self._logger = logging.getLogger( __programName__)
        self._api = "https://api.meetup.com/"
        self._params = {}
        self._params[ "key" ] = apikey
        self._items = items
        self._requester = MeetupRequest( self._items )
            
    def get_group(self, url_name ):
        
        return Reshaper.reshapeGroupDoc( self._requester.simple_request( self._api + url_name, params = self._params )[1] ) 

    def get_groups_by_url(self, urls ):
        for i in urls:
            yield self.get_group( i )
            
    def get_past_events(self, url_name ) :
        
        params = deepcopy( self._params )
        
        params[ "status" ]       = "past"
        params[ "group_urlname"] = url_name
        
        return self._requester.paged_request( self._api + "2/events", params, Reshaper.reshapeEventDoc )

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
        reqURL = MeetupRequest.makeRequestURL( url_name, "events", str( eventID ), "attendance")
        return self._requester.paged_request( reqURL, self._params )
    
    def get_upcoming_events(self, url_name ):
        
        params = deepcopy( self._params )
        params[ "status" ] = "upcoming"
        params[ "group_urlname"] = url_name
        
        return self._requester.paged_request( self._api + "2/events", params, Reshaper.reshapeEventDoc)
    
    def get_member_by_id(self, member_id ):

        ( _, body ) = self._requester.simple_request( self._api + "2/member/" + str( member_id ), params = self._params )
        
        return body
    
    def get_members(self , urls ):
        for i in urls:
            for member in self.__get_members( i ):
                yield member
                
    def __get_members(self, url_name ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
        params[ "page"]    = self._items
 
        return self._requester.paged_request( self._api + "2/members", params, Reshaper.reshapeMemberDoc)
    
    def get_groups(self ):
        '''
        Get all groups associated with this API key.
        '''
        self._logger.debug( "get_groups")
        return self._requester.paged_request(self._api + "self/groups",  self._params )
    
    def get_pro_groups(self  ):
        '''
        Get all groups associated with this API key.
        '''
        self._logger.debug( "get_pro_groups")
        
        return self._requester.paged_request( self._api + "pro/MongoDB/groups", self._params, Reshaper.reshapeGroupDoc )
    
    def get_pro_group_names( self ):
        for i in self.get_pro_groups() :
            yield i[ "urlname" ]
            
    def get_pro_members(self ):
        
        self._logger.debug( "get_pro_members")
        
        return self._requester.paged_request( self._api + "pro/MongoDB/members", self._params, Reshaper.reshapeMemberDoc)

    