'''
Created on 29 Mar 2017

@author: jdrumgoole
'''
from argparse import ArgumentParser


def make_mongodb_parser( args, parser ):
    
    parser = ArgumentParser( args, parents=[ parser ] )
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    return parser