mongo localhost:27017/TESTMUGS -eval "db.dropDatabase()"
mongorestore -d TESTMUGS --archive=$MROOT/tests/testmugs.tar.gz --gzip
nosetests -x
