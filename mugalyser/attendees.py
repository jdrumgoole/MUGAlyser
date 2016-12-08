'''
Created on 1 Nov 2016

@author: jdrumgoole
'''

from .mugdata import MUGData
        
class Attendees( MUGData ):
    
    def __init__(self, mdb ):
        '''
        Constructor
        '''
        super( Attendees, self ).__init__( mdb, "attendees")   
    
    def get_attendees(self, event_url):
        
        return self.find( { "info.event.event_url" : event_url })

        
    def get_all_attendees(self , q=None):
        
        return self.find( q )
    
    def summary( self, doc ):

        event = doc[ "info"][ "event" ]
        address = ""
        city = ""
        country = ""
        
        headline = self.oneline( doc )
        if "venue" in event:
            address = event[ "venue" ][ "address_1" ]
            city = event[ "venue"][ "city"]
            country = event[ "venue" ][ "country"]
            
        return "%s\n\taddress:%s\n\tcity:%s\n\tcountry: %s" % ( headline,
                                                                address,
                                                                city,
                                                                country )
        
    def oneline(self, doc ):
        member = doc[ "info" ][ "attendee"][ "member" ]
        event = doc[ "info"][ "event" ]
        
        return "name: %s, event:%s, date: %s, rsvp: %i" % ( member[ "name" ], 
                                                            event[ "name"], 
                                                            event[ "time" ],
                                                            event[ "yes_rsvp_count"])
