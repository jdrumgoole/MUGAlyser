PROG=$1
shift
PASSWORD=$1
shift
python $PROG --host "mongodb://jdrumgoole:${PASSWORD}@mugalyser-shard-00-00-ffp4c.mongodb.net:27017,mugalyser-shard-00-01-ffp4c.mongodb.net:27017,mugalyser-shard-00-02-ffp4c.mongodb.net:27017/MUGS?ssl=true&replicaSet=MUGAlyser-shard-0&authSource=admin" $*
