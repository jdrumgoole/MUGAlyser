# MUGAlyser

Version 0.8 Beta

Updated audit schema to make it more consistent. Added a utility
program to get info (called muginfo.py). Now data is read from a
MUGS.py file so no reading of files is required.  You can still get a
single MUG instance by using the --mug parameter.

Added support for replica set parameters so we can connect to Atlas.

There is now a very basic REST API for some of the functions in webgui.

VERSION : 0.9 beta

MUGAlyser is a python program that uses the Meetup API to extract longitudinal data from the Meetup website for a collection of meetup
groups. Its designed to capture MongoDB meetup information but it could be used to collect data on any group of meetups by changing the
list of urlnames in the mugs.py file. You can also get specific mugs
using the --mug parameter.

It puts the data in a MongoDB database. There are seperate collections for groups, members, past events and upcoming events. 

There is also an audit collection which tracks when the data was collected. Each record is associated with a Batch ID which is
tracked in the audit collection.

This is beta software. Not all combinations of options have been tested. 


```
JD10Gen-old:mugalyser jdrumgoole$ python mugalyser_main.py -h
usage: mugalyser_main.py [-h] [--database DATABASE] [--host HOST]
                         [--port PORT] [--username USERNAME]
                         [--password PASSWORD] [--replset REPLSET]
                         [--admindb ADMINDB] [--ssl] [--multi] [--verbose]
                         [-v] [--wait WAIT] [--trialrun]
                         [--mugs MUGS [MUGS ...]]
                         [--attendees ATTENDEES [ATTENDEES ...]]
                         [--loglevel LOGLEVEL]

A program to read data from the Meetup API into MongoDB

  Licensed under the AFGPL
  https://www.gnu.org/licenses/agpl-3.0.en.html

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE

optional arguments:
  -h, --help            show this help message and exit
  --database DATABASE   specify the database name [default: MUGS]
  --host HOST           hostname [default: localhost]
  --port PORT           port name [default: 27017]
  --username USERNAME   username to login to database
  --password PASSWORD   password to login to database
  --replset REPLSET     replica set to use [default: ]
  --admindb ADMINDB     Admin database used for authentication [default:
                        admin]
  --ssl                 use SSL for connections
  --multi               use multi-processing
  --verbose             set verbosity level [default: None]
  -v, --version         show program's version number and exit
  --wait WAIT           How long to wait between processing the next parallel
                        MUG request [default: 5]
  --trialrun            Trial run, no updates [default: False]
  --mugs MUGS [MUGS ...]
                        Process MUGs list list mugs by name or use "all"
  --attendees ATTENDEES [ATTENDEES ...]
                        Capture attendees for these groups
  --loglevel LOGLEVEL   Logging level [default: INFO]
JD10Gen-old:mugalyser jdrumgoole$ 
```
