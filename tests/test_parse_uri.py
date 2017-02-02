'''
Created on 31 Jan 2017

@author: jdrumgoole
'''

from pymongo.uri_parser import parse_uri

if __name__ == '__main__':
    uri = "mongodb://jdrumgoole:topsecret@mugalyser-shard-00-00-ffp4c.mongodb.net:27017,mugalyser-shard-00-01-ffp4c.mongodb.net:27017,mugalyser-shard-00-02-ffp4c.mongodb.net:27017/MUGS?ssl=true&replicaSet=MUGAlyser-shard-0&authSource=admin"
    result = parse_uri( uri )
    for k,v in result.iteritems() :
        print( "'%s':'%s'" % (k, v ))