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
        

def reshapeGeospatial( doc ):
    doc[ "location" ] = { "type" : "Point", "coordinates": [ doc[ "lon"], doc[ "lat"] ] }
    del doc[ 'lat']
    del doc[ 'lon']
    return doc 

def unpackMembers( members ):
    
    for i in members :
        # Can't use full stops in MDB keys
        yield reshapeGeospatial( i )

def noop( d ):
    return d
        
def paginator( r ):
    
    data = r.json()
    #pprint.pprint( data )
    
    if data[ 'meta' ]:
        for i in data[ "results"]:
            yield i
    
        while data[ 'meta' ][ "next" ] != "" :
            nextBatch = requests.get( data['meta'][ 'next' ])
            data = nextBatch.json()
        
            for i in data[ "results"]:
                yield i
    else:
        yield r 
        
class MUGAlyser(object):
    '''
    classdocs
    '''


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
        
        r = requests.get( self._api + url_name, params = params )
        
        return returnData( r )

            
    def makeRequest(self, req, params ):
        r = requests.get( req, params=params )
        logging.debug( "request: '%s'" % r.url )
            
        if r.raise_for_status() is None:
            return r
        
        
    def get_past_events(self, url_name, items=20 ) :
        
        params = deepcopy( self._params )
        
        params[ "status" ]       = "past"
        params[ "page" ]         = str( items )
        params[ "group_urlname"] = url_name
        
        r = self.makeRequest( self._api + "2/events", params = params )
        #r = requests.get( self._api + url_name + "/events", params = params )
        #print( "request: '%s'" % r.url )
        return paginator( r )

    def get_upcoming_events(self, url_name, items=20 ):
        
        params = deepcopy( self._params )
        params[ "status" ] = "upcoming"
        params[ "page"]    = str( items )
        params[ "group_urlname"] = url_name
        
        r = self.makeRequest( self._api + "2/events", params = params )
        #r = requests.get( self._api + url_name + "/events", params = params )
        print( "request: '%s'" % r.url )
        return paginator( r )
    
    def get_members(self, url_name, items=100, returnText=False ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
        params[ "page"]    = str( items )

        logging.debug( "get_members")
        r = self.makeRequest( self._api + "2/members", params = params )
        #r = requests.get( self._api + "2/members", params = params )
        
        return paginator( r )
    

