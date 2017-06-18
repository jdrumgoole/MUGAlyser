'''
Created on 8 Jun 2017

@author: jdrumgoole
'''
import unittest

from mugalyser.apikey import get_meetup_key
import requests

class Test(unittest.TestCase):


    def test_api_fail(self):
        params={}
        params[ "key" ] = get_meetup_key()
        #params[ "group_urlname" ] = "MongoDBGlasgow"
        params[ "group_urlname" ] = "London-MongoDB-User-Group"
        params[ "page"]    = 10
        count = 0
        print( "requests.get(%s, %s)" % ( "https://api.meetup.com/2/members", params ))
        r = requests.get( "https://api.meetup.com/2/members", params )
        count = count + 1 
        print( "requests count : %i" % count )
        print( r.url )
        _ = r.headers
        body = r.json()
        
        print( "results: %i" % len( body[ "results"]))
        for i in body[ "results"]:
            #print( i )
            pass
    
        #print( body[ "meta"])
        
        while ( body[ 'meta' ][ "next" ] != ""  ) :

            print( "requests.get(%s)" % body['meta'][ 'next' ] )
            r = requests.get( body['meta'][ 'next' ] )
            count = count + 1 
            print( "requests count : %i" % count )
            print( "next: %s" % r.url )
            print( "body: '%s'" % r.text )

            body = r.json()
            print( "results: %i" % len( body ))
        
            for i in body[ "results"]:
                #print( i )
                pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_api_fail']
    unittest.main()