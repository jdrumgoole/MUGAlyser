'''
Created on 7 Oct 2016

@author: jdrumgoole
'''
from pprint import pprint

from mugalyser.mugdata import MUGData
from utils.query import Query
import itertools

EU_COUNTRIES = [ "Austria", 
                 "Belgium", 
                 "Bulgaria", 
                 "Croatia", 
                 "Cyprus", 
                 "Czech Republic", 
                 "Denmark", 
                 "Estonia", 
                 "Finland", 
                 "France", 
                 "Germany", 
                 "Greece", 
                 "Hungary", 
                 "Ireland", 
                 "Italy", 
                 "Latvia", 
                 "Lithuania", 
                 "Luxembourg", 
                 "Malta", 
                 "Netherlands", 
                 "Poland", 
                 "Portugal", 
                 "Romania", 
                 "Slovakia", 
                 "Slovenia", 
                 "Spain", 
                 "Sweden", 
                 "United Kingdom" ]


class Groups(MUGData):
    '''
    classdocs
    '''

    def __init__(self, mdb ):
        
        super( Groups, self ).__init__( mdb, "groups")  

        
    def get_group(self, url_name ):
        return self.find_one( { "group.urlname": url_name })
    
    def get_all_groups(self, region=None):
        if region:
            if type( region ) is list:
                return self.find( { "group.country" : { "$in" : region }})
            else:
                raise ValueError( "region parameter is not a list (type = %s)" % type( region ))
        else:
            return self.find()
 
    def get_groups(self, group_names ):
        
        return itertools.chain( *[ self.get_group( i ) for i in group_names ] )
    
    def get_country_group_urlnames(self, country="USA"):
        return self.get_region_group_urlnames( [ country ])
    
    def get_region_group_urlnames(self, countries = EU_COUNTRIES ):
        return [ x[ "group"]["urlname" ] for x in self.find( {  "group.country" : { "$in" : countries }}) ]
            

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
        
    