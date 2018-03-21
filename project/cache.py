#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class Cache():
    """
    updates or loads a network json database object
    """

    def __init__(self):
        """
        basic minimum datastructure of json class db
        """
        self.db = {}
        self.db['routers'] = {}
        self.db['switches'] = {}

    def add_switch(self, switchname):
        """
        add a new switch dictionary
        """
        self.db['switches'][switchname] = {}

    def add_switch_entry(self, switchname, mac, mode, interface, vlan):
        """
        adds a new switch entry to class db
        """
        self.db['switches'][switchname][mac] = {}
        self.db['switches'][switchname][mac]['mode'] = mode
        self.db['switches'][switchname][mac]['interface'] = interface
        self.db['switches'][switchname][mac]['vlan'] = vlan

    def add_router(self, routername):
        """
        add a new router dictionary
        """
        self.db['routers'][routername] = {}

    def add_router_entry(self, routername, ip, mac, proto, age, vlan):
        """
        adds a new router entry to class db
        """
        self.db['routers'][routername][ip] = {}
        self.db['routers'][routername][ip]['ip'] = ip
        self.db['routers'][routername][ip]['mac'] = mac
        self.db['routers'][routername][ip]['proto'] = proto
        self.db['routers'][routername][ip]['age'] = age
        self.db['routers'][routername][ip]['vlan'] = vlan

    def time_clock(self, timetaken):
        """
        records time taken for poll into database
        """
        self.runtime = str(timetaken)

    @property
    def timetaken(self):
        """
        return last poller run time
        """
        return self.runtime

    def write_to_file(self):
        """
        writes the database to a file
        """
        db = {
            'db': self.db,
            'lastUpdate': datetime.now(),
            'pollTime': self.runtime
        }
        with open(args.cachedbfile, 'w') as outfile:
            json.dump(db, outfile, cls=DateTimeEncoder)

    @property
    def load_from_file(self):
        """
        loads the database from file
        """
        return ""
