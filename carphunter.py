#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# Written by Jonathan Kelley, March 7, 2018
# March 12, Added config support from yaml..

#pip2.7 install netmiko
#pip2.7 install --upgrade paramiko
#pip2.7 install cryptography
#pip2.7 uninstall gssapi
#pip2.7 install unidecode
###pip2.7 install yamlcfg
#pip2.7 install prettytable
###pip2.7 install configloader
#pip2.7 install loadconfig
import sys
from netmiko import ConnectHandler
from datetime import datetime
from unidecode import unidecode
import re
import json
from pprint import pprint
import prettytable
import argparse
from loadconfig import Config

parser = argparse.ArgumentParser(description="Cisco Arp Hunter v0.1", epilog="This Python based tool uses Netmiko to search your Cisco® branded routers and switches. This tool creates an ARP cache in a local json file (using --poll). --mac and -ip can be used to find MAC, IP, PORT and VLAN associations immediately against this json cache.")
parser.add_argument('-m', '--mac', action="store", dest="mac", help="Search json cache for MAC to port/vlan mappings")
parser.add_argument('-i', '--ip', action="store", dest="ip", help="Search json cache for IP address to MAC mapping")
parser.add_argument('--poll', action="store_true", default=False, dest="pollmode", help="Poll devices now and save to local json-cache-file")
parser.add_argument('--json', action="store_true", default=False, dest="json", help="Print output in JSON format")
parser.add_argument('--all-ports', action="store_true", default=False, dest="allports", help="List all ports in cache search including port channels")

parser.add_argument('--config', action="store", default="/etc/carphunter.yml", dest="configfile", help="Non-default config file location")
parser.add_argument('--json-cache-file', action="store", default="/mnt/data/arp.json", dest="cachedbfile", help="Non-default json-cache-file location")
args = parser.parse_args()

class ConfigHelper(object):
    """
    helper class to load configuration properties from local file
    """

    def __init__(self, path):
        conf = "!include {}".format(path)
        config = Config(conf)
        self.configuration = Config(conf)
    
    @property
    def raw(self):
        """
        returns raw configuration as python object, not really for external use.
        """
        return self.configuration

    @property
    def global_logins(self):
        """
        return tuple of user/password combintation for global switch login privileges.
        """
        return (self.configuration['global']['user'], self.configuration['global']['password'])

    @property
    def switches(self):
        """
        return a list of configuration properties for switching devices.
        """
        return self.configuration['devices']['switches']

    @property
    def routers(self):
        """
        return a list of configuration properties for routing devices.
        """
        return self.configuration['devices']['routers']

conf = ConfigHelper(path=args.configfile)

# netmiko device constants
a_device = {
    'device_type': 'cisco_ios',
    'verbose': False,
}

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

def device_command(device, command):
    """
    connects to a network device and issues a command, returns decoded split output
    """
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command(command)
    return unidecode(output).split("\n")

def poll_devices():
    """
    initiates a polling process and saves all device data to disk for cached searches in json
    """
    cache = Cache()
    start_benchmark = datetime.now()
    for router, v in conf.routers.iteritems():
        print("Collecting ARP from router {} ({})".format(router, v.get("name", "No name defined")))
        a_device['ip'] = router
        a_device['username'] = conf.global_logins[0]
        a_device['password'] = conf.global_logins[1]
        output = device_command(a_device, "show ip arp")
        cache.add_router(routername=v.get("name", router))
        for line in output:
            if "Internet" in line:
                line=re.split(" +",line)
                line = [x.strip() for x in line]
                dict = {}
                cache.add_router_entry(
                    routername=v.get("name", router), 
                    ip=line[1], 
                    age=line[2],
                    mac=line[3], 
                    proto=line[4],
                    vlan=line[5],
                    )

    for switch, v in conf.switches.iteritems():
        print("Collecting ARP from switch {} ({})".format(switch, v.get("name", "No name defined")))
        a_device['ip'] = switch
        a_device['username'] = v.get("user", conf.global_logins[0])
        a_device['password'] = v.get("password",conf.global_logins[1])
        output = device_command(a_device, "show mac address-table")
        cache.add_switch(switchname=v.get("name", switch))
        for line in output:
            line = line.strip() # strip unwanted spaces
            if ("STATIC" in line) or ("DYNAMIC" in line):
                line = line.split("    ")
                line = [x.strip() for x in line]
                dict = {}
                dict['vlan'] = line[0]
                dict['mac'] = line[1]
                dict['mode'] = line[2]
                dict['interface'] = line[3]
                cache.add_switch_entry(
                    switchname=v.get("name", switch), 
                    vlan=line[0], 
                    mac=line[1], 
                    mode=line[2],  
                    interface=line[3]
                    )

    end_benchmark = datetime.now()

    total_time = end_benchmark - start_benchmark
    dbs.time_clock(total_time)
    dbs.write_to_file()
    print("Time taken: {}".format(dbs.timetaken))

def print_statistics(data, total_time):
    print("\nStatistics:")
    print("  * Cache contains {} routers, {} switches".format(len(data['db']['routers']),len(data['db']['switches'])))
    print("  * Cache updated {}\n  * Last poller took {}".format(data['lastUpdate'], data['pollTime']))
    print("  * This lookup took {}".format(total_time))
    print("Tool written by: Jonathan Kelley")

def search_arp_table(search, jsondata=False):
    """
    searches the json cache for an arp entry
    """
    start_benchmark = datetime.now()
    print("Checking network for `{}`...".format(search))
    data = json.load(open(args.cachedbfile))
    for router, arpitem in data['db']['routers'].iteritems():
        print_results = 0
        #print router, arp
        table = prettytable.PrettyTable(["hwaddr", "ip", "vlan", "age", "proto"])
        for ip, values in arpitem.iteritems():
            if not values['vlan']:
                values['vlan'] = "N/A"
            if search in values['mac']:
                table.add_row([values['mac'], ip, values['vlan'], values['age'], values['proto']])
                print_results = 1
        if print_results:
            print("\nRouting Device: {} found match!".format(router))
            print("{}".format(table))
    for switch, arpitem in data['db']['switches'].iteritems():
        print_results = 0
        table = prettytable.PrettyTable(["hwaddr", "interface", "vlan", "mode"])
        for mac, values in arpitem.iteritems():
            if search in mac:
                if not args.allports:
                    if "/" in values['interface']:
                        table.add_row([mac, values['interface'], values['vlan'], values['mode']])
                        print_results = 1
                else:
                    table.add_row([mac, values['interface'], values['vlan'], values['mode']])
                    print_results = 1
        if print_results:
            print("\nSwitching Device: {} found match!".format(switch))
            print("{}".format(table))
    end_benchmark = datetime.now()

    total_time = end_benchmark - start_benchmark
    print_statistics(data, total_time)

def ip2arp(searchip,jsondata=False):
    """
    find arpa in json cache based on ip address
    """
    start_benchmark= datetime.now()
    if not jsondata:
        print("Checking network for `{}` ARPA entry...".format(searchip))
    data = json.load(open(args.cachedbfile))
    jsondata = {}
    for router, arpitem in data['db']['routers'].iteritems():
        print_results = 0
        exact_match = 0 # if exact match is found, hide ambiguous results
        #print router, arp
        jsondata[router] = {}
        table = prettytable.PrettyTable(["ip", "hwaddr", "vlan", "age", "proto"])
        for ip, values in arpitem.iteritems():
            if values['vlan'] == '':
                values['vlan'] = "?"
            if searchip == values['ip']:
                table.add_row([ip, values['mac'], values['vlan'], values['age'], values['proto']])
                print_results = 1
                exact_match = 1
            elif searchip in values['ip']:
                if not exact_match:
                    table.add_row([ip, values['mac'], values['vlan'], values['age'], values['proto']])
                    print_results = 1
        if print_results:
            print("\nRouting Device: {} found a matching IP!".format(router))
            print("{}\n".format(table))
            print("")
    end_benchmark = datetime.now()
    total_time = end_benchmark - start_benchmark
    if not jsondata:
        print_statistics(data, total_time)

if "__main__" == __name__:
    # arg parse
    if len(sys.argv) == 1:
        # Ask for y/n if displaying ALL NETWORK DATA
        yes = {'yes','y', 'ye'}
        no = {'no','n', ''}
        sys.stdout.write("WARNING : This will display ALL NETWORK INFORMATION, are you sure?\n")
        sys.stdout.write("   Type 'yes' or 'no': ")
        choice = raw_input().lower()
        if choice in yes:
           pass
        elif choice in no:
            print("Exiting...")
            exit(1)
        else:
           sys.stdout.write("Please respond with 'yes' or 'no'")
    if args.pollmode:
        # --poll flag
        print("Collection polling started. Do not terminate or data will not be saved.")
        poll_devices()
    else:
        # not --poll flag
        if args.ip:
            # --ip flag
            ip2arp(args.ip, args.json)
        else:
            # --mac flag
            if not args.mac:
                args.mac = "."
            search_arp_table(args.mac)


