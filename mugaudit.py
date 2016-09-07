'''
Created on 6 Sep 2016

@author: jdrumgoole
'''
import meetup.api
import pymongo
import datetime

class Mug_Audit(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        pass
        
       
import pprint

if __name__ == "__main__" :
    
    
    meetup_groups= { "London-MongoDB-User-Group"  : None, 
                     "DublinMUG"                  : None, 
                     "Paris-MongoDB-User-Group"   : None }
    
    meetup_API_key = "4a1e51774664e3412136d6457522120"
    
    client = meetup.api.Client( meetup_API_key )
    
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
        
    
    
