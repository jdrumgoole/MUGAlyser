'''
Created on 6 Sep 2016

@author: jdrumgoole
'''

import logging
import pprint

from copy import deepcopy

from mugalyser.version import __programName__
from mugalyser.meetup_request import MeetupRequest
from mugalyser.reshape import Reshape_Event, Reshape_Pro_Group, Reshape_Group, Reshape_Member


def makeRequestURL(*args):
    url = "https://api.meetup.com"

    for i in args:
        url = url + "/" + i

    return url


class MeetupAPI(object):
    '''
    classdocs
    '''

    def __init__(self, apikey, page=200, reshape=None):
        '''
        Constructor
        '''

        self._logger = logging.getLogger(__programName__)
        self._api = "https://api.meetup.com/"
        self._params = {}
        self._params["key"] = apikey
        self._params["page"] = page
        self._reshape = reshape
        self._requester = MeetupRequest()

    def get_group(self, url_name):

        (url, _, group) = self._requester.simple_request(self._api + url_name, params=self._params)

        if self._reshape:
            return (url, Reshape_Group(group).reshape())
        else:
            return (url, group)

    def get_groups_by_url(self, urls):
        for i in urls:
            yield self.get_group(i)

    def get_all_attendees(self, groups=None):
        groupsIterator = None
        if groups:
            groupsIterator = groups
        else:
            groupsIterator = self.get_groups()

        for group in groupsIterator:
            return self.get_attendees(group)

    def get_attendees(self, url_name):

        for url, event in self.get_past_events(url_name):
            # pprint.pprint(event)
            # print(event["id"])
            for _, attendee in self.get_event_attendees(event["id"], url_name):
                yield (url, {"attendee": attendee, "event": event})

    def get_event_attendees(self, eventID, url_name):

        # https://api.meetup.com/DublinMUG/events/62760772/attendance?&sign=true&photo-host=public&page=20
        reqURL = makeRequestURL(url_name, "events", str(eventID), "attendance")
        return self._requester.paged_request(reqURL, self._params)

    def get_upcoming_events(self, url_name):

        params = deepcopy(self._params)
        params["status"] = "upcoming"
        params["group_urlname"] = url_name

        return self._requester.paged_request(self._api + "2/events", params)

    def get_past_events(self, url_name):

        params = deepcopy(self._params)

        params["status"] = "past"
        params["group_urlname"] = url_name

        if self._reshape:
            return ((url, Reshape_Event(i).reshape()) for (url, i) in
                    self._requester.paged_request(self._api + "2/events", params))
        else:
            return self._requester.paged_request(self._api + "2/events", params)

    def get_member_by_id(self, member_id):

        (url, _, body) = self._requester.simple_request(self._api + "2/member/" + str(member_id), params=self._params)

        if self._reshape:
            return (url, Reshape_Member(body).reshape())
        else:
            return (url, body)

    def get_members(self, urls):
        for i in urls:
            # print( "processing: %s" % i )
            for (url, member) in self.__get_members(i):
                # print("processing: %s" % member[ "name"])
                yield (url, member)

    def __get_members(self, url_name):

        params = deepcopy(self._params)
        params["group_urlname"] = url_name

        if self._reshape:
            return ((url, Reshape_Member(i).reshape()) for (url, i) in
                    self._requester.paged_request(self._api + "2/members", params))
        else:
            return self._requester.paged_request(self._api + "2/members", params)

    def get_groups(self):
        '''
        Get all groups associated with this API key.
        '''
        self._logger.debug("get_groups")

        if self._reshape:
            return ((url, Reshape_Group(i).reshape()) for (url, i) in
                    self._requester.paged_request(self._api + "self/groups", self._params))
        else:
            return self._requester.paged_request(self._api + "self/groups", self._params)

    def get_pro_groups(self):
        '''
        Get all groups associated with this API key.
        '''
        self._logger.debug("get_pro_groups")

        if self._reshape:
            return ((url, Reshape_Pro_Group(i).reshape()) for (url, i) in
                    self._requester.paged_request(self._api + "pro/MongoDB/groups", self._params))
        else:
            return self._requester.paged_request(self._api + "pro/MongoDB/groups", self._params)

    def get_pro_group_names(self):
        for (url, i) in self.get_pro_groups():
            # print("pro name:'{}'".format(i["urlname"]))
            yield i["urlname"]

    def get_pro_members(self):

        self._logger.debug("get_pro_members")
        # print( self._params )

        if self._reshape:
            return ((url, Reshape_Member(i).reshape()) for (url, i) in
                    self._requester.paged_request(self._api + "pro/MongoDB/members", self._params))
        else:
            return self._requester.paged_request(self._api + "pro/MongoDB/members", self._params)
