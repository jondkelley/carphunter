#!/usr/bin/env python
# -*- coding: utf-8 -*-

# cisco specific library functions

from datetime import date, datetime
import json
import prettytable


def print_statistics(data, total_time):
    print("\nStatistics:")
    print("  * Cache contains {} routers, {} switches".format(
        len(data['db']['routers']), len(data['db']['switches'])))
    print("  * Cache updated {}\n  * Last poller took {}".format(
        data['lastUpdate'], data['pollTime']))
    print("  * This lookup took {}".format(total_time))

def search_arp_table(args):
    """
    searches the json cache for an arp entry
    """
    start_benchmark = datetime.now()
    print("Checking network for `{}`...".format(args.ip))
    data = json.load(open(args.cachedbfile))
    for router, arpitem in data['db']['routers'].iteritems():
        print_results = 0
        #print router, arp
        table = prettytable.PrettyTable(
            ["hwaddr", "ip", "vlan", "age", "proto"])
        for ip, values in arpitem.iteritems():
            if not values['vlan']:
                values['vlan'] = "N/A"
            if args.mac in values['mac']:
                table.add_row([values['mac'], ip, values['vlan'],
                               values['age'], values['proto']])
                print_results = 1
        if print_results:
            print("\nRouting Device: {} found match!".format(router))
            print("{}".format(table))
    for switch, arpitem in data['db']['switches'].iteritems():
        print_results = 0
        table = prettytable.PrettyTable(
            ["hwaddr", "interface", "vlan", "mode"])
        for mac, values in arpitem.iteritems():
            if args.mac in mac:
                if not args.allports:
                    if "/" in values['interface']:
                        table.add_row([mac, values['interface'],
                                       values['vlan'], values['mode']])
                        print_results = 1
                else:
                    table.add_row([mac, values['interface'],
                                   values['vlan'], values['mode']])
                    print_results = 1
        if print_results:
            print("\nSwitching Device: {} found match!".format(switch))
            print("{}".format(table))
    end_benchmark = datetime.now()

    total_time = end_benchmark - start_benchmark
    print_statistics(data, total_time)


def ip2arp(args):
    """
    find arpa in json cache based on ip address
    """
    start_benchmark = datetime.now()
    if not args.json:
        print("Checking network for `{}` ARPA entry...".format(args.ip))
    data = json.load(open(args.cachedbfile))
    jsondata = {}
    for router, arpitem in data['db']['routers'].iteritems():
        print_results = 0
        exact_match = 0  # if exact match is found, hide ambiguous results
        #print router, arp
        jsondata[router] = {}
        table = prettytable.PrettyTable(
            ["ip", "hwaddr", "vlan", "age", "proto"])
        for ip, values in arpitem.iteritems():
            if values['vlan'] == '':
                values['vlan'] = "?"
            if args.ip == values['ip']:
                table.add_row([ip, values['mac'], values['vlan'],
                               values['age'], values['proto']])
                print_results = 1
                exact_match = 1
            elif args.ip in values['ip']:
                if not exact_match:
                    table.add_row(
                        [ip, values['mac'], values['vlan'], values['age'], values['proto']])
                    print_results = 1
        if print_results:
            print("\nRouting Device: {} found a matching IP!".format(router))
            print("{}\n".format(table))
            print("")
    end_benchmark = datetime.now()
    total_time = end_benchmark - start_benchmark
    if not args.json:
        print_statistics(data, total_time)


def print_table(header, values):
    table = prettytable.PrettyTable(header)
    table.add_row(values)
    print(table)
