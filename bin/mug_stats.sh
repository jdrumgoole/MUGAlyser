#!/bin/bash

# Creates csv file with the following fields for a given database
# Provide database name as first argument
# csv file will be <databaseName>.csv

echo "Name, Member_count, Upcoming_Events, Past_Events, Urlname, Link" > $1.csv
	
mongo $1 --quiet --eval "
	db.groups.find().forEach(function(doc) {
		var name = doc.group.name.replace(/,/g, '');
		var member_count = doc.group.members;
		var past_events_count = db.past_events.find({'event.group.name': name}).count();
		var upcoming_events_count = db.upcoming_events.find({'event.group.name': name}).count();
		var url = doc.group.urlname;
		var link = doc.group.link;
		var vals = [name, member_count, past_events_count, upcoming_events_count, url, link];
		print(vals);
	})
" >> $1.csv