'''
Created on 7 Oct 2016

@author: jdrumgoole
'''
from pprint import pprint

from .mugdata import MUGData

class Groups(MUGData):
    '''
    classdocs
    '''

    def __init__(self, mdb ):
        
        super( Groups, self ).__init__( mdb, "groups")  

        
    def get_group(self, url_name ):
        return self.find_one( { "group.urlname": url_name })
    
    def get_all_groups(self):
        cursor = self.find()
        
        for g in cursor :
            yield g
 
    def get_meetup_groups(self, group_names ):
        
        for i in group_names:
            yield self.get_group( i )   

    @staticmethod
    def summary( g ):
        return u"name: {0}\nmembers:{1}\ncountry: {2}\n".format( g[ "name" ], 
                                                                g[ "members" ], 
                                                                g[ "country" ])
    
    
    @staticmethod
    def printGroup( group, output="short" ):
        
        if output == "short" :
            print( group[ 'name' ] )
        elif output == "summary" :
            print( Groups.summary( group ))
        else:
            pprint( group )
        
    