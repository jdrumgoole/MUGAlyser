#!/bin/sh
if [ -d "MUGALYSER_BUILD" ]; then
	mv MUGALYSER_BUILD MUGALYSER_BUILD.$$
fi

if [ $MEETUP_API_KEY == "" ]; then
	echo "MEETUP_API_KEY is not defined"
	exit 2
fi

mkdir -p MUGALYSER_BUILD
cd MUGALYSER_BUILD
git clone https://github.com/jdrumgoole/MUGAlyser.git
virtualenv mugalyser_env
source mugalyser_env/bin/activate
pip install --upgrade pip
pip install pymongo
pip install requests
pip install mongodb_utils
pip install pydrive
cd MUGAlyser
pushd mugalyser
python ../bin/makeapikeyfile_main.py --apikey $MEETUP_API_KEY 
if [ $? -eq 2 ]; then
        echo "makeapikeyile.py failed to generateed a key"
	exit 2
fi
popd
python setup.py test
if [ $? -ne 0 ]; then
        echo "python setup test failed"
        exit 2
fi
python setup.py install
if [ $? -ne 0 ]; then
        echo "python setup install failed"
        exit 2
fi
