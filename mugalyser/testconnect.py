'''
Created on 11 Oct 2016

@author: jdrumgoole
'''

import pymongo
from argparse import ArgumentParser


if __name__ == '__main__':
    
    parser = ArgumentParser()
    
    parser.add_argument( "--host", default="mongodb://localhost:27017" )
    
    args = parser.parse_args()
    
    client = pymongo.MongoClient( host=args.host )
    
    db = client[ "test" ]
    collection = db[ "collection"]
    collection.insert_one( { "a" : "b"} )
    print("Connection successful")
    
    
    