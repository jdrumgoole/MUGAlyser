'''
Created on 8 Jun 2017

@author: jdrumgoole
'''
import unittest

from mugalyser.meetup_api import MeetupRequest
from mugalyser.apikey import get_meetup_key
import requests

class Test(unittest.TestCase):


    def test_api_fail(self):
        params={}
        params[ "key" ] = get_meetup_key()
        params[ "group_urlname" ] = "MongoDBGlasgow"
        params[ "page"]    = 10
 
        r = requests.get( "https://api.meetup.com/2/members", params )
        print( r.url )
        headers = r.headers
        body = r.json()
        
        print( "results: %i" % len( body[ "results"]))
        for i in body[ "results"]:
            print( i )
    
        print( body[ "meta"])
        count = 0
        while ( body[ 'meta' ][ "next" ] != ""  ) :

            #print( "makeRequest (old): %i" % count )
            r = requests.get( body['meta'][ 'next' ] )
            print( "next: %s" % r.url )
            print( "body: %s" % r.text )

            body = r.json()
            print( "results: %i" % len( body ))
            count = count + 1

        
            for i in body[ "results"]:
                print( i )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_api_fail']
    unittest.main()