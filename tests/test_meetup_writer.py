'''
Created on 5 Dec 2016

@author: jdrumgoole
'''
import unittest

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.meetup_writer import MeetupWriter
from mugalyser.apikey import get_meetup_key
from mugalyser.audit import Audit
from mugalyser.version import __version__, __programName__

def setup_database( name ):
    mdb = MUGAlyserMongoDB( uri = "mongodb://localhost/" + name )
    audit = Audit( mdb )
    batchID = audit.startBatch( { "args"    : None, 
                                  "version" : __programName__ + " " + __version__ },
                                  trial = False,
                                  apikey=get_meetup_key())
        
    writer = MeetupWriter( audit )
    writer.capture_snapshot( "DublinMUG" )
        
    audit.endBatch( batchID )
    return mdb
     
class Test_meetup_writer(unittest.TestCase):

    def test_get_one(self):
        setup_database( "TEST_DATA_MUGS")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    
    unittest.main()