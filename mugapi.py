'''
Created on 6 Sep 2016

@author: jdrumgoole
'''
import meetup.api
import pymongo
import datetime



class MUG_API(object):
    '''
    classdocs
    '''

    API_KEY = "4a1e51774664e3412136d6457522120"
    
    def __init__(self, api_key =  API_KEY  ):
        '''
        Constructor
        '''
        self._meetup_client = meetup.api.Client( api_key )
 
        
    def get_mugs( self, member_id ):
        '''
         Get a list of all the MUGS that a user is registered for.
         '''
        
        groups = self._meetup_client.GetGroups({'member_id': member_id } )
            
        return groups.results
    
    
    def get_events(self, group_id, status="upcoming" ):
        
        events = self._meetup_client.GetEvents( { "group_id" : group_id, "status" : status }) 
        
        return events[ "results" ]
        
    def get_members(self, group_id ):
        
        members = self._meetup_client.GetMembers( { "group_id" : group_id })
        
        
        
        
        
        
       
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
        
    
    
