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
        return r.json()
        
def makeRequest( req, params=None ):
    logger = logging.getLogger()
    level = logger.getEffectiveLevel()
    
    logger.setLevel( logging.WARN )
    
    r = requests.get( req, params=params )
    #logging.debug( "request: '%s'" % r.url )
        
    try:
        return returnData( r )
    except requests.HTTPError, e :

        logger.error( "HTTP Error  : %s:" % e )
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
 
def paginator( r, func=None):
    
    if func is None:
        func = noop
        
    data = r
    #pprint.pprint( data )
    
    if data[ 'meta' ]:
        for i in data[ "results"]:
            yield func( i )
    
        while data[ 'meta' ][ "next" ] != "" :
            nextBatch = makeRequest( data['meta'][ 'next' ])
            data = nextBatch
        
            for i in data[ "results"]:
                yield  func( i )
    else:
        yield r 
        
class MUGAlyser(object):
    '''
    classdocs
    '''

    def __init__(self, api_key = MEETUP_API_KEY, ratePerHr = 200 ):
        '''
        Constructor
        '''
        
        self._api = "https://api.meetup.com/"
        self._params = {}
        self._params[ "key" ] = api_key
        self._params[ "sign"] = "true"
        

    def get_group(self, url_name ):
        
        params = deepcopy( self._params )
        
        return makeRequest( self._api + url_name, params = params )  

    def get_past_events(self, url_name, items=20 ) :
        
        params = deepcopy( self._params )
        
        params[ "status" ]       = "past"
        params[ "page" ]         = str( items )
        params[ "group_urlname"] = url_name
        
        r = makeRequest( self._api + "2/events", params = params )
        #r = requests.get( self._api + url_name + "/events", params = params )
        #print( "request: '%s'" % r.url )
        return paginator( r )

    def get_upcoming_events(self, url_name, items=20 ):
        
        params = deepcopy( self._params )
        params[ "status" ] = "upcoming"
        params[ "page"]    = str( items )
        params[ "group_urlname"] = url_name
        
        r = makeRequest( self._api + "2/events", params = params )
        #r = requests.get( self._api + url_name + "/events", params = params )
        #print( "request: '%s'" % r.url )
        return paginator( r  )
    
    def get_members(self, url_name, items=100, returnText=False ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
        params[ "page"]    = str( items )

        logging.debug( "get_members")
        r = makeRequest( self._api + "2/members", params = params )
        #r = requests.get( self._api + "2/members", params = params )
        
        return paginator( r, reshapeGeospatial )
    

