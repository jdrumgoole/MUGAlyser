'''
Created on 6 Sep 2016

@author: jdrumgoole
'''
import meetup.api
import pymongo
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
    
    mongo_groups = client.GetGroups({'member_id': "99473492" })
    
    #mongo_groups = client.GetGroups({'lat': "51.326530", "lon" : "7.000413", "radius" : "100" })
    results = mongo_groups.results 
    
    print( "type: %s" % type( results ))
    print( "len: %d" % len( results ))
    
    MuGList = []
    
    pprint.pprint( results[0] )
    for k in results:
        MuGList.append( k )
            
    print( "Total no of MUGs: %d" % len( MuGList) )
    
    for k in MuGList :
        if k[ "organizer"]["name"] == "MongoDB" :
            print( "Found: '%s'" % k['urlname'] )
            groups.insert_one( { "name" : k[ "urlname"], "info" : k } )

#     for k,v in mongo_groups.__dict__.iteritems():
#         print( "k: %s" % k )
#         print( "v: %s" % v ) 

