import argparse
import pymongo
import pprint
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument( "--host", default="mongodb://localhost:27017", help="Connect to mongodb server")
    parser.add_argument( "--database", default="source_prod", help="default database")
    parser.add_argument("--collection", default="Leads", help="Connect collection")
    parser.add_argument("--query", type=dict, default={}, help="query")
    parser.add_argument("--findone", type=bool,default=False, store_value=True, default="findOne query")
    args = parser.parse_args()

    client = pymongo.MongoClient( host=args.host)

    print( "Connecting to '{}.{}".format( args.database, args.collection))
    db = client[args.database]
    col = db[args.collection]
    if args.findOne:
        doc = col.findOne( args.query)
        if doc:
            pprint.pprint(doc)
        else:
            print("No docs found")
    else:
        cursor = col.find(args.query)
        for i in cursor:
            pprint.pprint(i)
