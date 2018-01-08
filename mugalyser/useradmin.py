import pymongo
import pprint
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument( "--host", default="mongodb://localhost:27017",
                         help="URI for connecting to MongoDB [default: %(default)s]" )
    parser.add_argument( "--command", default="listusers")
    parser.add_argument( "--username" )
    parser.add_argument( "--password" )
    parser.add_argument( "--database", default="test" )

    args = parser.parse_args()
    client = pymongo.MongoClient( host = args.host )
    database = client[ args.database ]


    if args.command == "listusers" :
        print( "Users for database '%s'" % args.database )
        users = database.command( "usersInfo" )[ "users"]
        #pprint.pprint( users )
        for i in users:
            pprint.pprint( i )
    elif args.command == "adduser" :
        if args.username:
            try:
                result = database.command("createUser", args.username, args.password,
                                          roles=[{'role': 'readWrite', 'db': args.database}])
                print(result)
            except pymongo.errors.OperationFailure as e:
                print(e)


    elif args.command == "deleteuser" :
        pass
