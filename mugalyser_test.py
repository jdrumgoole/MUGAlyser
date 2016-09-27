'''
Created on 26 Sep 2016

@author: jdrumgoole
'''
from mugalyser import MUGAlyser
from apikey import MEETUP_API_KEY
import pprint
import json

if __name__ == '__main__':
    
    mlyser = MUGAlyser( api_key = MEETUP_API_KEY )
    
    group = mlyser.get_group( "DublinMUG" )
    
    #pprint.pprint( group )
    #pprint.pprint( dir ( group ))

    events = mlyser.get_past_events( "DublinMUG" )
    
    #pprint.pprint( events[0] )
    
    members = mlyser.get_members( "DublinMUG" )
    
    total = 0
    for batch in members :
        print( "Batch size  : %i" % len( batch ))
        total = total + len( batch )
        print( "Total batch : %i" % total )

    