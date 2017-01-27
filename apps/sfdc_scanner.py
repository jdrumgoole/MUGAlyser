'''
Created on 22 Jan 2017

@author: jdrumgoole
'''
from argparse import ArgumentParser
from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.agg import Agg
from mugalyser.members import Members

from pprint import pprint

if __name__ == '__main__':
    
    parser = ArgumentParser()
        
    parser.add_argument( "--host", default="mongodb://localhost:27017/MUGS", 
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    
    args = parser.parse_args()
    
    mdb = MUGAlyserMongoDB( uri=args.host )
    
    db = mdb.database()
    
    members = Members( mdb )
    
    sfdc_collection = db[ "sfdc" ]
    
    aggs = Agg( sfdc_collection )
    
    count = 0
    
    for i in members.find():
        #pprint( i )
        names  = i[ "member" ]["member_name"].split()
        
        if len( names ) > 2 :
            print( "Long name: %s" % names )
        elif len( names ) < 2 :
            print( "Short name: %s" % names )
            continue
        
        cursor = sfdc_collection.find( { "First Name" : names[ 0 ],
                                         "Last Name" : names[ 1 ] } )
        

        for sfdc in cursor :
            print( "matched : SFDC" )
            pprint( sfdc )
            print( "Meetup")
            pprint( i )
            count = count + 1
            
        
    print( "Matched : %i"% count  )