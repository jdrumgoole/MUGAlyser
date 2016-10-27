'''
Created on 6 Sep 2016

@author: jdrumgoole
'''

import requests
import logging
from copy import deepcopy
from mugs import MUGS

from apikey import get_meetup_key

from pprint import pprint

def convert( meetupObj ):
    
    retVal = {}
    for i in dir( meetupObj  ) :
        if not i.startswith( "__"):
            obj = getattr( meetupObj, i, None )
            retVal[ i ] = obj
            
    return retVal


def returnData( r ):
    if r.raise_for_status() is None:
        return ( r.headers, r.json())
        
def makeRequest( req, params=None ):
    logger = logging.getLogger()
    level = logger.getEffectiveLevel()
    
    logger.setLevel( logging.WARN ) # turn of info output for requests
    
    r = requests.get( req, params=params )
    #print( "url: '%s'" % r.url )
    #print( "text: %s" % r.text )
    #print( "headers: %s" % r.headers )
    try:
        return returnData( r )
    except requests.HTTPError, e :

        logger.error( "HTTP Error  : %s:", e )
        raise
    finally:
        logger.setLevel( level )
        
def reshapeGeospatial( doc ):
    doc[ "location" ] = { "type" : "Point", "coordinates": [ doc["lon"], doc["lat" ]] }
    del doc[ 'lat']
    del doc[ 'lon']
    return doc


def noop( d ):
    return d
 
 
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

def paginator( headers, body, params=None, func=None):
    '''
    Meetup API returns results as pages. The old API embeds the 
    page data in a meta data object in the response object. The new API
    returns page data in the Header info. 
    
    Func is a function that takes a doc and returns a doc. Right now
    we use this to reshape geospatial coordinates into a format that MongoDB
    understands.
    '''
    
    #print( "paginatorEntry( %s )" % headers )
    if func is None:
        func = noop
        
    data = body
    #pprint.pprint( data )
    
    # old style format 
    if "meta" in body :
        for i in body[ "results"]:
            yield func( i )
    
        while data[ 'meta' ][ "next" ] != "" :
            data = makeRequest( data['meta'][ 'next' ])[1]
        
            for i in data[ "results"]:
                yield  func( i )
    elif ( "Link" in headers ) : #new style pagination
        for i in data :
            yield func( i )
            
        ( link, rel ) = getHeaderLink( headers[ "Link"] )
        while ( rel != "prev") : # no next link in last page
            #print( "rel : %s" % rel )
            #print( "link: %s" % link )
            ( headers, body ) = makeRequest( link, params=params )
            #print( "paginatorLoop( %s )" % headers )
            ( link, rel ) = getHeaderLink( headers[ "Link"] )
            #print( "rel: '%s'" % rel )
            for i in data :
                yield  func( i )


    else: # new style but we have all the data
        for i in data:
            yield func( i )
        
class MUGAlyser(object):
    '''
    classdocs
    '''
    @staticmethod
    def makeRequestURL( *args ):
        url = "https://api.meetup.com"
        
        for i in args:
            url = url + "/" + i
            
        return url
    
    def __init__(self, api_key = get_meetup_key()):
        '''
        Constructor
        '''
        
        self._api = "https://api.meetup.com/"
        self._params = {}
        self._params[ "key" ] = api_key
        self._params[ "sign"] = "true"
        

    def get_groups(self):
        for i in MUGS:
            yield i
            
    def get_group(self, url_name ):
        
        params = deepcopy( self._params )
        
        return makeRequest( self._api + url_name, params = params )[1]  

    def get_past_events(self, url_name, items=20 ) :
        
        params = deepcopy( self._params )
        
        params[ "status" ]       = "past"
        params[ "page" ]         = str( items )
        params[ "group_urlname"] = url_name
        
        (header, body) = makeRequest( self._api + "2/events", params = params )
        #r = requests.get( self._api + url_name + "/events", params = params )
        #print( "request: '%s'" % r.url )
        return paginator( header, body, params )


    def get_attendees( self, groups=None, items=50 ):
        
        groupsIterator = None
        if groups :
            groupsIterator = groups
        else:
            groupsIterator = self.get_groups()
            
        for group in groupsIterator :
            for event in self.get_past_events( group ):
                #pprint( event )
                for attendee in self.get_event_attendees(event[ "id"], group, items ):
                    yield ( attendee, event )
    
            
    def get_event_attendees(self, eventID, url_name, items=20 ):
        params = deepcopy( self._params )
        params[ "page" ] = str( items )
        
        #https://api.meetup.com/DublinMUG/events/62760772/attendance?&sign=true&photo-host=public&page=20
        reqURL = MUGAlyser.makeRequestURL( url_name, "events", str( eventID ), "attendance")

        ( header, body ) = makeRequest( reqURL, params=params)

        return paginator( header, body, params )
    
    def get_upcoming_events(self, url_name, items=20 ):
        
        params = deepcopy( self._params )
        params[ "status" ] = "upcoming"
        params[ "page"]    = str( items )
        params[ "group_urlname"] = url_name
        
        ( header, body ) = makeRequest( self._api + "2/events", params = params )
        #r = requests.get( self._api + url_name + "/events", params = params )
        #print( "request: '%s'" % r.url )
        return paginator(  header, body, params )
    
    def get_members(self, url_name, items=100 ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
        params[ "page"]    = str( items )

        logging.debug( "get_members")
        ( header, body ) = makeRequest( self._api + "2/members", params = params )
        #r = requests.get( self._api + "2/members", params = params )
        
        return paginator( header, body, params, reshapeGeospatial )
    

