# MUGAlyser

Version "1.0.6a6"




MUGAlyser is a python program that uses the Meetup API to extract
longitudinal data from the Meetup website for a collection of meetup
groups. Its designed to capture MongoDB meetup information but it
could be used to collect data on any group of meetups by changing the
list of urlnames in the mugs.py file. You can also get specific mugs
using the --mug parameter.

It puts the data in a MongoDB database. There are seperate collections
for groups, members, past events and upcoming events. 

There is also an audit collection which tracks when the
data was collected. Each record is associated with a Batch ID which is
tracked in the audit collection.

This is beta software and is currently a WIP. It may break at any time.

The bin directory contains the most interesting programs for end
users.

## bin/mugalyser_main.py

Captures data from meetup via the Meet API. For this program to work
you need to provide a [ meetup api key ](
https://secure.meetup.com/meetup_api/key/).  Without this key the
program will fail. The key can be passed in via the `--apikey`
argument. Most people find it easier to set an environment variable
`MEETUP_API_KEY` which the program will also use.

The meetup API is rate limited and the program is smart about the rate
limit so you should see issues unless you run more than one copy at a
time.

It currently takes about 17 minutes to capture a complete batch of
meetup data for the MongoDB user groups (of which there at 116 with
over 50k members in total).

The mugalyser can use the Meetup Pro API calls if you have a [pro
account](https://www.meetup.com/pro/).  You can ask the MUAlyser to
use pro or no pro accounts using the `--collect` argument. The options
are `pro`, `nopro` and `all`.  The default is `all`.

The list of MUGs to process is read from a file using the `--urlfile`
parameter. There is a default list of pro accounts in
`../etc/mongodb_pro_groups`.

By default the data is written to the `MUGS` database. To change this
default specify a different database via the [MongoDB URI](https://docs.mongodb.com/manual/reference/connection-string/) passed to the
`--host` argument.

## bin/makeapikeyfile.py

This creates a file callled `apikey.py` which contains the API key for
the applcation. The API key can be passed in on the command line or
read from `MEETUP_API_KEY`. `apikey.py` is not checked into github
to prevent they key from being compromised.






```
JD10Gen-old:mugalyser jdrumgoole$ python bin/mugalyser_main.py -h
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
