'''
Created on 10 Oct 2016

Simple program to Dump group data..

@author: jdrumgoole
'''
from argparse import ArgumentParser
from mugs import MUGS

def getCountryMugs( mugs, country ):
    for k,v in mugs.iteritems() :
        if v[ "country"] == country :
            yield (v[ "country"], k )
            
if __name__ == '__main__':
            
        parser = ArgumentParser()
        
        parser.add_argument( "-g", "--hasgroup", nargs="+", default=[], help="Is this a MongoDB Group")
        
        parser.add_argument( "-l", "--listgroups", action="store_true", default=False,  help="print out all the groups")
        
        parser.add_argument( "-c", "--listcountry", nargs="+", default=[],  help="print groups by country")
        args = parser.parse_args()
        
        for i in args.hasgroup:
            if i in MUGS:
                print( "{:30} :is a MongoDB MUG".format( i ))
            else:
                print( "{:30} :is not a MongoDB MUG".format( i ))
            
        if args.listgroups:
            for k,v in MUGS.iteritems():
                print( "{:35} (location: {})".format( k,v["country"] ))
            print( "%i total" % len( MUGS ))
            
        count = 0
        for i in args.listcountry:
            byCountry = getCountryMugs( MUGS, i )
            for k,v in byCountry :
                count = count +1
                print( "{:20} has MUG: {}".format( k, v ))
            print( "%i total" % count )
            
                
        