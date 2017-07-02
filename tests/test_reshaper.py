'''
Created on 30 Jun 2017

@author: jdrumgoole
'''
import unittest
import datetime
import copy


from mugalyser.reshape import Reshaper, Reshape_Group, Reshape_Member


class Test(unittest.TestCase):

    #
    # This is the Dublin MUG object captured from https://secure.meetup.com/meetup_api/console/?path=/:urlname
    # on the 1-Jul-2017.
    #
    DublinMUG = {
        "id": 3478392,
        "name": "Dublin MongoDB User Group",
        "link": "https://www.meetup.com/DublinMUG/",
        "urlname": "DublinMUG",
        "description": "<p>This group is a place for developers in Dublin to learn more about the dynamic schema, open source, document database MongoDB. So if you are facing challenges with MySQL, Postgres or Oracle and want to explore a more flexible, scalable alternative, please join us at one of our monthly sessions.</p>",
        "created": 1331746826000,
        "city": "Dublin",
        "country": "IE",
        "localized_country_name": "Ireland",
        "state": "",
        "join_mode": "open",
        "visibility": "public",
        "lat": 53.33,
        "lon": -6.25,
        "members": 845,
        "organizer": {
            "id": 191179165,
            "name": "Francesca Krihely",
            "bio": "",
            "photo": {
                "id": 248723623,
                "highres_link": "https://secure.meetupstatic.com/photos/member/5/c/4/7/highres_248723623.jpeg",
                "photo_link": "https://secure.meetupstatic.com/photos/member/5/c/4/7/member_248723623.jpeg",
                "thumb_link": "https://secure.meetupstatic.com/photos/member/5/c/4/7/thumb_248723623.jpeg",
                "type": "member",
                "base_url": "https://secure.meetupstatic.com"
                }
            },
        "who": "Members",
        "group_photo": {
            "id": 281358162,
            "highres_link": "https://secure.meetupstatic.com/photos/event/4/6/f/2/highres_281358162.jpeg",
            "photo_link": "https://secure.meetupstatic.com/photos/event/4/6/f/2/600_281358162.jpeg",
            "thumb_link": "https://secure.meetupstatic.com/photos/event/4/6/f/2/thumb_281358162.jpeg",
            "type": "event",
            "base_url": "https://secure.meetupstatic.com"
        },
        "key_photo": {
            "id": 448848272,
            "highres_link": "https://secure.meetupstatic.com/photos/event/b/c/9/0/highres_448848272.jpeg",
            "photo_link": "https://secure.meetupstatic.com/photos/event/b/c/9/0/600_448848272.jpeg",
            "thumb_link": "https://secure.meetupstatic.com/photos/event/b/c/9/0/thumb_448848272.jpeg",
            "type": "event",
            "base_url": "https://secure.meetupstatic.com"
        },
        "timezone": "Europe/Dublin",
        "category": {
            "id": 34,
            "name": "Tech",
            "shortname": "Tech",
            "sort_name": "Tech"
        }
    }
    

    def test_reshape_time(self):

        # times in meetup are MS
        # 1498843646 is seconds since epopch 
        doc = { "a" : 1, "b" : 2, "c"  : 1498843646 * 1000 }
        #>>> time.ctime( 1498843646 )
        #'Fri Jun 30 18:27:26 2017'
        
        new_doc = Reshaper.reshape_time_doc(doc, "c" )
        self.assertEqual( new_doc[ 'c'], datetime.datetime(2017, 6, 30, 18, 27, 26))
        
    def test_reshape_geospatial(self):
        
        doc = { "a" : 1, "b" : 2, "lon"  : -115.3, "lat" : 36.2 }
        
        new_doc = Reshaper.reshape_geospatial_doc( doc, "location", [ "lon" , "lat"])
        
        self.assertEqual( new_doc["location"]["coordinates"], [ -115.3, 36.2 ])
        
        new_doc = Reshaper.reshape_geospatial_doc( copy.deepcopy( self.DublinMUG), "location", [ "lon" , "lat"])
        self.assertEqual( new_doc["location"]["coordinates"], [ -6.25, 53.33 ])
                
    def test_reshape_member(self):
        
        
        doc_list = []
        for _ in range( 20 ):
            doc_list.append( { "a" : 1, "b" : 2, "joined" : 1498843646 * 1000, 
                              "join_time": 1498843646 * 1000, "last_access_time"  : 1498843646 * 1000,
                              "lat" : 53.33,
                              "lon" : -6.25 } )
            
        for i in doc_list:
            doc = Reshape_Member( i ).reshape()
            self.assertTrue( isinstance( doc[ "joined"], datetime.datetime ))
            
    def test_reshape_group(self):
        
        groups = [ ]
        for i in range( 5 ):
            groups.append( copy.deepcopy( self.DublinMUG ))
            
        for i in groups :
            doc = Reshape_Group( i ).reshape()
            self.assertEqual( doc["location"]["coordinates"], [ -6.25, 53.33 ])
            self.assertTrue( isinstance( doc[ "created"], datetime.datetime ))
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_reshape_time']
    unittest.main()