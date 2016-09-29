'''
Created on 26 Sep 2016

@author: jdrumgoole
'''
from mugalyser import MUGAlyser
from apikey import MEETUP_API_KEY

import pprint 

def count( gen ):
    
    total=0
    
    for i in gen :
        print( "Batch size  : %i" % len( i ))
        total = total + len( i )
        print( "Total batch : %i" % total )
        
if __name__ == '__main__':
    
    mlyser = MUGAlyser( api_key = MEETUP_API_KEY )
    
    group = mlyser.get_group( "DublinMUG" )
    
    #pprint.pprint( group )
    #pprint.pprint( dir ( group ))

    events = mlyser.get_past_events( "DublinMUG" )
    
    for i in events:
        print( i[ 'name' ] )
    
    count( events )
    #pprint.pprint( events[0] )
    
    members = mlyser.get_members( "DublinMUG" )
    pprint.pprint( dir ( group ))
    count( members )


    