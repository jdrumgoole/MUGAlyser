'''
Created on 13 May 2017

@author: jdrumgoole
'''
from mugalyser import meetup_api
import pprint
if __name__ == '__main__':
    
    m = meetup_api.MeetupAPI()
    
    i = 0
    get_count =0
    while True:
        get_count = get_count + 1
        try :
            it = m.get_members( "DublinMUG")
        except ValueError :
            print( "ValueError")
            
        for member in it:
            i =i+1
            #pprint.pprint( member )
            print( "%i %i: %s" % ( get_count, i, member[ "name" ] ))