'''
Created on 7 Feb 2017

@author: jdrumgoole
'''

from mugalyser.mongodb import MUGAlyserMongoDB
from argparse import ArgumentParser
import pprint

if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument( '--host', default="mongodb://localhost:27017/MUGS", help='URI to connect to : [default: %(default)s]')
    
    args = parser.parse_args()
    mugdb = MUGAlyserMongoDB( args.host )
    db = mugdb.database()
    result = db.command( { "ismaster" : 1 })
    pprint.pprint( result )