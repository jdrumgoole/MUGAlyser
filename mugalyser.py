'''
Created on 6 Sep 2016

@author: jdrumgoole
'''
import meetup.api
import pymongo
import datetime
import requests
import json

from copy import deepcopy

from   apikey import MEETUP_API_KEY


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
            
    def get_past_events(self, url_name,returnText=False):
        
        params = deepcopy( self._params )
        params[ "status" ] = "past"
        params[ "page"]    = "20"
        r = requests.get( self._api + url_name + "/events", params = params )
        
        if r.raise_for_status() is None:
            if returnText :
                return r.text
            else:
                return r.json()
    
    
    def get_members(self, url_name, items=100, returnText=False ):
        
        params = deepcopy( self._params )
        params[ "group_urlname" ] = url_name
        params[ "page"]    = str( items )

        r = requests.get( self._api + "2/members", params = params )
        print( r.url )
        meta = r.json()[ "meta"]

        yield returnData( r, returnText )

        while meta[ "next" ] != "" :
            nextBatch = requests.get( meta[ 'next' ])
            meta = nextBatch.json()["meta"]
            yield returnData( nextBatch, returnText )        
        
    def get_mugs( self, member_id ):
        '''
         Get a list of all the MUGS that a user is registered for.
         '''
        
        groups = self._meetup_client.GetGroups({'member_id': member_id } )
            
        return groups.results
        
        
        
       
import pprint

if __name__ == "__main__" :
    
    
    meetup_groups= { "London-MongoDB-User-Group"  : None, 
                     "DublinMUG"                  : None, 
                     "Paris-MongoDB-User-Group"   : None }
    

    
    client = meetup.api.Client( meetup_API_key  )
    
    mclient = pymongo.MongoClient()
    db = mclient.MUGAudit
    mugs = db.MuGs
    groups = db.GroupState
    
    for k,v in meetup_groups.iteritems() : 
        
        print("Getting info for group: '%s'" % k )
        group_info = client.GetGroup({'urlname': k })
        
        if not mugs.find_one(  { "_id" : k }):
            mugs.insert_one( { "_id" : k } )
        meetup_groups [ k ]  = group_info
        
        print( "Member count: %s" % group_info.members )
        pprint.pprint( group_info.__dict__ )
        
        groups.insert_one( { "MuG"  : k,
                             "ts"   : datetime.datetime.now(),
                             "info" : group_info.__dict__  })
        
    
    
