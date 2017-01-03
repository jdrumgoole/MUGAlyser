# Overview of the MUGAlyser Database

The main database containing all the collections is called MUGS.

(We recommend examining the database using the [MongoDB Compass tool](
https://www.mongodb.com/products/lp/compass)).

Within the MUGS database there are six  collections:

* **audit** : A tracking collection for each run of the mugalyser
* **members** : The list of all members associated with the MongoDB pro group
* **groups** : All the Meetup groups associated with the MongoDB pro group
* **attendees** : All the members who have attended events in the past
* **past_events** : All the events that have already happened
* **upcoming_events** : All the events that are about to happen

## Audit Collection

With each execution of the [mugalyser_main.py](https://github.com/jdrumgoole/MUGAlyser/blob/master/mugalyser/mugalyser_main.py) program a new batch is
created in the **audit** collection. As records are added to each of
the collections they are embedded inside a **batch** document.
Here is an example.

```
> db.members.findOne({}, { "_id":0, "member.member_name" : 1, timestamp:1, batchID:1 } )
{
	"member" : {
		"member_name" : "Ramya Varkala"
	},
	"timestamp" : ISODate("2017-01-03T21:53:54.065Z"),
	"batchID" : 1
}
>
```

Within the **audit** collection there is a locator document for
finding the current batch.

```
> db.audit.findOne()
{
	"_id" : ObjectId("586c1d6c0cb2350488fedbc1"),
	"name" : "Current Batch",
	"currentID" : 1,
	"batchID" : 0,
	"valid" : false,
	"schemaVersion" : "1.0.1 alpha",
	"timestamp" : ISODate("2017-01-03T21:53:48.398Z")
}
>
```

It is identifed by the **name** __"Current Batch"__ and a**batchID**
of 0. The **currentID** field defines the batch that was run.

## members collection

The members collection contains all the member information these
records are created by the PRO meetup API call
[get members](https://www.meetup.com/meetup_api/docs/pro/:urlname/members/).
You will need a PRO enabled
[meetup API key](https://secure.meetup.com/meetup_api/key/) to allow
this request to succeeed.

All the meetup API requests are contained in [meetup_api.py](
https://github.com/jdrumgoole/MUGAlyser/blob/master/mugalyser/meetup_api.py)
class.

You can use the
[Meetup API console](https://secure.meetup.com/meetup_api/console/?path=/pro/:urlname/members)
to see the output format.

We do some basic post processing at the API level. The two key
functions are converting meetup time objects to datetime objects that
can be inserted in a way that MongoDB prefers and collecting lat/long
coordinates into a point object which MongoDB also prefers. 




