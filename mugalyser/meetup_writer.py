"""
Created on 21 Nov 2016

@author: jdrumgoole
"""
from requests import HTTPError

import logging

import datetime
# import pprint

from mugalyser.meetup_api import MeetupAPI
from mugalyser.version import __programName__


def mergeEvents(writer):
    for attendee, event in writer:
        yield {u"attendee": attendee,
               u"event": event}


def feedback(doc):
    print(".")
    logger = logging.getLogger(__programName__)
    if doc.has_key("name"):
        logger.info("Processing: %s", doc['name'])
    else:
        logger.info("Processing: .")


class MeetupWriter(object):
    """
    A class that reads data about MUGS from the Meetup API using the MeetupAPI class and writes that
    data to a MongoDB collection. Supports pro and no pro APIs
    
    The process function is a generic reader function that takes a retrieval generator (provided by
    the MeetupAPI class and a processing function. It iterates over the docs returned by the
    retrieval generator and transforms then with "processFunc". The results are returned in an 
    embedded document with the key "newFieldname".
    
    """

    INSERT_SIZE = 1000

    def _addTimestamp(self, doc):

        if "timestamp" in doc:
            raise ValueError("cannot add timestamp, \
                              'timestamp' field already exists")

        if "batchID" in doc:
            raise ValueError("cannot add batchID, \
                              'batchID' field already exists")

        doc["timestamp"] = datetime.datetime.utcnow()
        doc["batchID"] = self._batch_ID

        return doc

    def __init__(self, apikey, batch_ID, mdb, reshape=True, unordered=True):
        """Write contents of meetup API to MongoDB"""

        self._mdb = mdb
        self._meetup_api = MeetupAPI(apikey, reshape=reshape)
        self._batch_ID = batch_ID
        self._groups = self._mdb.groupsCollection()
        self._members = self._mdb.membersCollection()
        self._attendees = self._mdb.attendeesCollection()
        self._pastEvents = self._mdb.pastEventsCollection()
        self._upcomingEvents = self._mdb.upcomingEventsCollection()
        #         self._mugs = []
        self._unordered = unordered
        self._members_set = set()

        self._logger = logging.getLogger(__programName__)

    def update_members(self, retrievalGenerator, processFunc):
        '''
        For nopro collections we count the members in each group. To avoid double counting
        we use update to overwrite previous records with the same member.
        '''

        docs = []
        count = 0

        # print( "update_members")
        for url, i in retrievalGenerator:

            # ignore already inserted members a member may be in multiple
            # groups.
            if self._members.find_one({"batchID": self._batch_ID,
                                       "id": i["id"]}):
                continue
            else:
                # print( "inserting : %s" %i["id"] )
                count = count + 1
                docs.append(processFunc(i))
                if count == 500:
                    self._members.insert_many(docs)
                    docs = []
                    count = 0

        if count > 0:
            self._members.insert_many(docs)
            docs = []
            count = 0

    def write(self, collection, retrievalGenerator, processFunc):
        """

        :param collection: The collection to write too
        :param retrievalGenerator: a generator that produces docs
        :param processFunc: a preprocessing function for the docs to be written
        :return: The number of docs written
        """
        '''
        Use retrievalGenerator to get a single
        document (this should be a generator function). Use processFunc to tranform the 
        document into a new doc (it should take a doc and return a doc).
        Write the new doc using the newFieldName.
        
        Write is done using a generator as well. The write receiver accumulates writes until a threshold
        is reached and then writes them as a batch using BatchWriter.
        
        '''

        docs = []
        count = 0
        # print( "write")
        for url, i in retrievalGenerator:
            docs.append(processFunc(i))
            if len(docs) == MeetupWriter.INSERT_SIZE:
                count = count + len(docs)
                # print( "inserted 500")
                collection.insert_many(docs)
                docs = []

        if len(docs) > 0:
            collection.insert_many(docs)
            count = count + len(docs)
        return count

    def write_Attendees(self, group):

        writer = self._meetup_api.get_attendees(group)

        self.write(self._attendees, writer, self._addTimestamp)

    #     def write_group(self, url_name, groupName="group"):
    #         group = self._meetup_api.get_group( url_name )
    #         newDoc = self._addTimestamp( groupName, group )
    #         self._groups.insert_one( newDoc )
    #         return newDoc

    #     def updateGroup(self, groupName, doc ):
    #         self._mugs.append( doc[ "urlname" ])
    #
    #         return self._addTimestamp( groupName, doc )

    def write_nopro_groups(self, mug_list):
        groups = self._meetup_api.get_groups_by_url(mug_list)
        self.write(self._groups, groups, self._addTimestamp)

    def select_groups(self, groups, urls):
        for url, g in groups:
            if g["urlname"] in urls:
                # print(g["urlname"])
                yield url, g

    # def write_pro_groups(self, urls):
    #
    #     groups = self._meetup_api.get_pro_groups()
    #     self.write(self._pro_groups, self.select_groups(groups, urls), self._addTimestamp)

    def write_groups(self, urls):
        """
        The old pro API has been disabled by the numbskulls at Meetup so no both
        pro and no pro APIs use the same get_group call.
        :param urls: List of  urlnames to get group info for
        :return: No of groups written
        """
        groups = self._meetup_api.get_groups_by_url(urls)
        return self.write(self._groups, groups, self._addTimestamp)
        # self.write_nopro_groups(urls)
        # if collect == "nopro":
        #     self.write_nopro_groups(urls)
        # elif collect == "pro":
        #     self.write_pro_groups(urls)
        # else:
        #     self.write_pro_groups(urls)
        #     self.write_nopro_groups(urls)

    def write_PastEvents(self, url_name):

        pastEvents = self._meetup_api.get_past_events(url_name)
        self.write(self._pastEvents, pastEvents, self._addTimestamp)

    def write_UpcomingEvents(self, url_name):
        upcomingEvents = self._meetup_api.get_upcoming_events(url_name)
        self.write(self._upcomingEvents, upcomingEvents, self._addTimestamp)

    # def write_pro_members(self):
    #     members = self._meetup_api.get_pro_members()
    #     self.write(self._pro_members, members, self._addTimestamp)
    #
    # def write_nopro_members(self, urls):
    #     members = self._meetup_api.get_members(urls)
    #     self.update_members(members, self._addTimestamp)

    def write_members(self, urls):
        members = self._meetup_api.get_members(urls)
        self.update_members(members, self._addTimestamp)
        # if collect == "nopro":
        #     self.write_nopro_members(urls)
        # elif collect == "pro":
        #     self.write_pro_members()
        # else:
        #     self.write_pro_members()
        #     self.write_nopro_members(urls)

    #     def mug_list(self):
    #         return self._mugs

    def capture_snapshot(self, url_name, admin_arg, phases):

        try:
            for i in phases:
                if i == "pastevents":
                    self._logger.info("process past events for      : '%s'", url_name)
                    self.write_PastEvents(url_name)
                elif i == "upcomingevents":
                    self._logger.info("process upcoming events for  : '%s'", url_name)
                    self.write_UpcomingEvents(url_name)
                elif i == "attendees":
                    if admin_arg:
                        self._logger.info("process attendees            : '%s'", url_name)
                        self.write_Attendees(url_name)
                    else:
                        self._logger.warning("You have not specified the admin arg")
                        self._logger.warning("You must be a meetup admin user to request attendees")
                        self._logger.warning("Ignoring phase 'attendees'")

                else:
                    self._logger.warn("ignoring phase '%s': not a valid execution phase", i)

        except HTTPError as e:
            self._logger.fatal("Stopped processing: %s", e)
            raise
