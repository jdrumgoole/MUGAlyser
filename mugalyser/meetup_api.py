'''
Created on 6 Sep 2016

@author: jdrumgoole
'''

import requests
import logging
import datetime
import time
import pprint

from copy import deepcopy

from mugalyser.apikey import get_meetup_key

from mugalyser.version import __programName__

def returnData( r ):
    if r.raise_for_status() is None:
        return ( r.headers, r.json())
        

class PaginatedRequest( object ):
    
    def __init__(self, items=500, logurl = False ):

        self._logurl = logurl
        self._items = 500
        
    def makeRequest(self, req, params ):
        logger = logging.getLogger( __programName__ )
    
        if self._logurl:
            print( "URL    : '%s'" % req )
            print( "params : '%s" % params )
            
        level = logger.getEffectiveLevel()
        
        logger.setLevel( logging.WARN ) # turn of info output for requests
        
        r = requests.get( req, params )
        logging.debug( "request URL   :'%s'", r.url )
        logging.debug( "request header: '%s'", r.headers )
        #print( "url: '%s'" % r.url )
        #print( "text: %s" % r.text )
        #print( "headers: %s" % r.headers )


        try:
            data = returnData( r )
            limit = int( data[0][ "X-RateLimit-Remaining"] )
            if  limit < 5 : #brute force, we can be more clever about this
                time.sleep( 1 )
                
            x={}
            
#             for k,v in data[1].items():
#     
#                 if type( v ) is unicode :
#                     x[ k ] = v
#                     print( "unicode")
#                 else:
#                     x[ k ] = str( v ).encode( 'utf8')
#                     print( "encoded")
#             #logging.debug( "return value: %s", data )
            return data
        
        except ValueError :
            print( "ValueError in makeRequests:")
            print( "request: '%s'" % r.url)
            print( "headers" )
            pprint.pprint( r.headers )
            print( "text" )
            pprint.pprint( r.text )
            raise
        
        except requests.HTTPError, e :
    
            logger.error( "HTTP Error  : %s:", e )
            raise
            
        finally:
            logger.setLevel( level )


            
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
    
    def paginatedRequest(self, req, params, reshaperFunc=None ):
        '''
        Takes a request and hands it off to the paginator API. It does this by initiating the request
        to get the first document back and then using it to look for headers.
        '''

        #print( "Intiate paginated request")    
        (header, body) = self.makeRequest( req, params )

        #print( "Paginator")
        #r = requests.get( self._api + url_name + "/events", params = params )
        #print( "request: '%s'" % r.url )
        #print( "header: '%s' )
        return self.paginator( header, body, params, func=reshaperFunc  )
    
    def paginator( self, headers, body, params, func=None, arg=None ):
        '''
        Meetup API returns results as pages. The old API embeds the 
        page data in a meta data object in the response object. The new API
        returns page data in the Header info. 
        
        Func is a function that takes a doc and returns a doc. Right now
        we use this to reshape geospatial coordinates into a format that MongoDB
        understands and to convert  meetup timestamps to datetime objects.
        
        paginator is a generator which yields results.
        
        '''
        
        #print( "paginatorEntry( %s )" % headers )
        if func is None:
            func = Reshaper.noop
            
        data = body
        #pprint.pprint( data )
        
        # old style format 
        if "meta" in body :
            for i in body[ "results"]:
                yield func( i )
        
            count = 0
            while ( data[ 'meta' ][ "next" ] != ""  ) :

                #print( "makeRequest (old): %i" % count )
                data = self.makeRequest( data['meta'][ 'next' ], params )[1]
                count = count + 1

            
                for i in data[ "results"]:
                    yield  func( i )
    
                    
        elif ( "Link" in headers ) : #new style pagination
            for i in data :
                yield func( i )
               
            count = 0 
            ( nxt, _) = self.getNextPrev(headers)
    
            count = 0
            while ( nxt is not None ) : # no next link in last page

                count = count + 1 
                #print( "make request (new): %i" % count )
                    
                ( headers, body ) = self.makeRequest( nxt, params )
                ( nxt, _ ) = self.getNextPrev(headers)
                for i in body :
                    yield  func( i )
    
        else: # new style but we have all the data
            for i in data:
                yield func( i )

def epochToDatetime( ts ):
    return datetime.datetime.fromtimestamp( ts /1000 )

class Reshaper( object ):
    
    def __init__(self ):
        self._reshape = {}
        
    def add( self, key, value ):
        self._reshape[ key] = value
        
    @staticmethod
    def noop( d, arg=None):
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
        return Reshaper.reshapeTime( Reshaper.reshapeGeospatial(doc), [ "join_time", "last_access_time" ])

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



    

        
    
def getHeaderLink( header ):
    #print( "getHeaderLink( %s)" % header )

    if "," in header:
        ( nxt, _ ) = header.split( ",", 2 )
    else:
        nxt = header
        
    ( link, relParam ) = nxt.split( ";", 2 )
    ( _, relVal ) = relParam.split( "=", 2 )
    link = link[1:-1] # strip angle brackets off link
    relVal = relVal[ 1:-1] # strip off quotes
    return ( link, relVal )


        
class MeetupAPI(object):
    '''
    classdocs
    '''
    @staticmethod
    def makeRequestURL( *args ):
        url = "https://api.meetup.com"
        
        for i in args:
            url = url + "/" + i
            
        return url
    
    def __init__(self, apikey = get_meetup_key(), items=500, logurl=False):
        '''
        Constructor
        '''
        
        self._api = "https://api.meetup.com/"
        self._params = {}
        self._params[ "key" ] = apikey
        self._items = str( items )
        self._requester = PaginatedRequest( self._items, logurl )
            
    def get_group(self, url_name ):
        
        params = deepcopy( self._params )
        
        return Reshaper.reshapeGroupDoc( self._requester.makeRequest( self._api + url_name, params = params )[1] ) 

    def get_past_events(self, url_name, items=20 ) :
        
        params = deepcopy( self._params )
        
        params[ "status" ]       = "past"
        params[ "page" ]         = self._items
        params[ "group_urlname"] = url_name
        
        return self._requester.paginatedRequest( self._api + "2/events", params, Reshaper.reshapeEventDoc )

    def get_all_attendees(self, groups=None, items=50 ):
        groupsIterator = None
        if groups :
            groupsIterator = groups
        else:
            groupsIterator = self.get_groups()
            
        for group in groupsIterator :
            return self.get_attendees(group, items)
        
    def get_attendees( self, url_name, items=50 ):
        
        for event in self.get_past_events( url_name ):
            #pprint( event )
            for attendee in self.get_event_attendees(event[ "id"], url_name, items ):
                yield ( attendee, event )
    
            
    def get_event_attendees(self, eventID, url_name, items=20 ):
        params = deepcopy( self._params )
        params[ "page" ] = self._items
        
        #https://api.meetup.com/DublinMUG/events/62760772/attendance?&sign=true&photo-host=public&page=20
        reqURL = self.makeRequestURL( url_name, "events", str( eventID ), "attendance")
        return self._requester.paginatedRequest( reqURL, params )
    
    def get_upcoming_events(self, url_name, items=20 ):
        
        params = deepcopy( self._params )
        params[ "status" ] = "upcoming"
        params[ "page"]    = self._items
        params[ "group_urlname"] = url_name
        
        return self._requester.paginatedRequest( self._api + "2/events", params, Reshaper.reshapeEventDoc)
    
    def get_member_by_id(self, member_id ):
        params = deepcopy( self._params )

        ( _, body ) = self._requester.makeRequest( self._api + "2/member/" + str( member_id ), params = params )
        
        return body
    
    def get_members(self, url_name, items=1000 ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
        params[ "page"]    = self._items

        return self._requester.paginatedRequest( self._api + "2/members", params )
    
    def get_groups(self, items=200 ):
        '''
        Get all groups associated with this API key.
        '''
        
        params = deepcopy( self._params )
        params[ "page" ]         = self._items
        logging.debug( "get_groups")
        return self._requester.paginatedRequest(self._api + "self/groups",  params )
    
    def get_pro_groups(self, items=20 ):
        '''
        Get all groups associated with this API key.
        '''
        
        params = deepcopy( self._params )
        params[ "page" ]         = self._items
        logging.debug( "get_pro_groups")
        
        return self._requester.paginatedRequest( self._api + "pro/MongoDB/groups", params, Reshaper.reshapeGroupDoc )
    
    def get_pro_members(self, items=200 ):
        params = deepcopy( self._params )
        params[ "page" ] = self._items
        logging.debug( "get_pro_members")
        
        return self._requester.paginatedRequest( self._api + "pro/MongoDB/members", params, Reshaper.reshapeMemberDoc)

    
    def get_pro_group_names( self ):
        for i in self.get_pro_groups() :
            yield i[ "urlname" ]
    