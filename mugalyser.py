'''
Created on 6 Sep 2016

@author: jdrumgoole
'''
import meetup.api
import pymongo
import datetime
import requests


from copy import deepcopy

from apikey import MEETUP_API_KEY


def convert( meetupObj ):
    
    retVal = {}
    for i in dir( meetupObj  ) :
        if not i.startswith( "__"):
            obj = getattr( meetupObj, i, None )
            retVal[ i ] = obj
            
    return retVal


def returnData( r, returnText = False ):
    if r.raise_for_status() is None:
        if returnText :
            return r.text
        else:
            return r.json()[ "results" ]
        
def listinator( l ):
    for i in l :
        yield i
    
def paginator( r, returnText = False ):
    
    meta = r.json()[ "meta"]

    yield returnData( r, returnText )

    while meta[ "next" ] != "" :
        nextBatch = requests.get( meta[ 'next' ])
        meta = nextBatch.json()["meta"]
        yield returnData( nextBatch, returnText ) 
        
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
        

    def get_group(self, url_name, returnText=False ):
        
        params = deepcopy( self._params )
        
        r = requests.get( self._api + url_name, params = params )
        
        if r.raise_for_status() is None:
            if returnText :
                return r.text
            else:
                return r.json()
            
    def makeRequest(self, req, params, log=True):
        r = requests.get( req, params=params )
        if log:
            print( "request: '%s'" % r.url )
            
        if r.raise_for_status() is None:
            return r
        
        
    def get_past_events(self, url_name, items=200 ):
        
        params = deepcopy( self._params )
        params[ "status" ] = "past"
        params[ "page"]    = str( items )
        
        #r = self.makeRequest( self._api + url_name + "/events", params = params )
        r = requests.get( self._api + url_name + "/events", params = params )
        print( "request: '%s'" % r.url )
        return listinator( r.json() )

    
    def get_members(self, url_name, items=100, returnText=False ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
        params[ "page"]    = str( items )

        r = self.makeRequest( self._api + "2/members", params = params )
        #r = requests.get( self._api + "2/members", params = params )

        return paginator( r, returnText )
        
    
