# MUGAlyser

VERSION : 0.5 beta

MUGAlyser is a python program that uses the Meetup API to extract longitudinal data from the Meetup website for a collection of meetup
groups. Its designed to capture MongoDB meetup information but it could be used to collect data on any group of meetups by changing the
list of urlnames in the MUGFILE.

It puts the data in a MongoDB database. There are seperate collections for groups, members, past events and upcoming events. 

There is also an audit collection which tracks when the data was collected. Each record is associated with a Batch ID which is
tracked in the audit collection.

This is beta software. Not all combinations of options have been tested. Specifically I haven't tested 
usernames and passwords for the db yet.


```
JD10Gen-old:MUGAlyser jdrumgoole$ python mugalyser_main.py -h
usage: mugalyser_main.py [-h] [--database DATABASE] [--host HOST]
                         [--port PORT] [--username USERNAME]
                         [--password PASSWORD] [--admindb ADMINDB] [--ssl]
                         [-v] [-V] [--mugfile MUGFILE] [--mug MUG]
                         [--trialrun] [--loglevel LOGLEVEL]

mugalyser_main -- Grab MUG Stats and stuff them into a MongoDB Database

  Licensed under the AFGPL
  https://www.gnu.org/licenses/agpl-3.0.en.html

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE

optional arguments:
  -h, --help           show this help message and exit
  --database DATABASE  specify the database name [default: MUGS]
  --host HOST          hostname [default: localhost]
  --port PORT          port name [default: 27017]
  --username USERNAME  username to login to database
  --password PASSWORD  password to login to database
  --admindb ADMINDB    Admin database used for authentication [default: admin]
  --ssl                use SSL for connections
  -v, --verbose        set verbosity level [default: None]
  -V, --version        show program's version number and exit
  --mugfile MUGFILE    List of MUGs stored in [default: None]
  --mug MUG            Process a single MUG [default: None]
  --trialrun           Trial run, no updates [default: False]
  --loglevel LOGLEVEL  Logging level [default: INFO]
JD10Gen-old:MUGAlyser jdrumgoole$ 
```
