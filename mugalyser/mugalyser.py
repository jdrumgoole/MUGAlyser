'''
Created on 6 Sep 2016

@author: jdrumgoole
'''

import requests
import logging
from copy import deepcopy


from apikey import MEETUP_API_KEY

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
    
    #print( "paginatorEntry( %s )" % headers )
    if func is None:
        func = noop
        
    data = body
    #pprint.pprint( data )
    
    if ( "Link" in headers ) :
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

    elif "meta" in body :
        for i in body[ "results"]:
            yield func( i )
    
        while data[ 'meta' ][ "next" ] != "" :
            data = makeRequest( data['meta'][ 'next' ])[1]
        
            for i in data[ "results"]:
                yield  func( i )
    else:
        yield data
        
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
    
    def __init__(self, api_key = MEETUP_API_KEY ):
        '''
        Constructor
        '''
        
        self._api = "https://api.meetup.com/"
        self._params = {}
        self._params[ "key" ] = api_key
        self._params[ "sign"] = "true"
        

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
    

