#!/bin/sh

cmd() {
    cmd=$1
    shift
    args=$*
    $cmd $args
    status=$?
    if [ $status -ne 0 ]; then
        echo "$cmd $args failed (status: $status)"
        exit $status
    fi
}
if [ -d "MUGALYSER_BUILD" ]; then
	mv MUGALYSER_BUILD MUGALYSER_BUILD.$$
fi

if [ $MEETUP_API_KEY == "" ]; then
	echo "MEETUP_API_KEY is not defined"
	exit 2
fi

mkdir -p MUGALYSER_BUILD
cd MUGALYSER_BUILD
git clone https://github.com/jdrumgoole/mongodb_utils.git
git clone https://github.com/jdrumgoole/MUGAlyser.git
virtualenv mugalyser_env
source mugalyser_env/bin/activate
pip install --upgrade pip
pip install pymongo
pip install requests
pip install pydrive
pushd bin
cmd "python" "makeapikeyfile_main.py" "--apikey $MEETUP_API_KEY"
popd
cmd "python" "setup.py" "test"
cmd "python" "setup.py" "install"

