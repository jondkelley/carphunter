#!/usr/bin/env python
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
import re


def device_command(device, command):
    """
    connects to a network device and issues a command, returns decoded split output
    """
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command(command)
    return unidecode(output).split("\n")


# netmiko device constants
a_device = {
    'device_type': 'cisco_ios',
    'verbose': False,
}


def poll_devices():
    """
    initiates a polling process and saves all device data to disk for cached searches in json

    todo asap: build a mock/testable contract output
    make 
    db = {}
    db['routers'] = {}
    and then use another function for the pretty table
    """
    cache = Cache()
    a_device = NMDeviceObject()

    start_benchmark = datetime.now()

    for router, v in conf.routers.iteritems():
        print("Collecting ARP from router {} ({})".format(
            router, v.get("name", "No name defined")))
        a_device['ip'] = router
        a_device['username'] = conf.global_logins[0]
        a_device['password'] = conf.global_logins[1]
        output = device_command(a_device, "show ip arp")
        cache.add_router(routername=v.get("name", router))
        for line in output:
            if "Internet" in line:
                line = re.split(" +", line)
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
        print("Collecting ARP from switch {} ({})".format(
            switch, v.get("name", "No name defined")))
        a_device['ip'] = switch
        a_device['username'] = v.get("user", conf.global_logins[0])
        a_device['password'] = v.get("password", conf.global_logins[1])
        output = device_command(a_device, "show mac address-table")
        cache.add_switch(switchname=v.get("name", switch))
        for line in output:
            line = line.strip()  # strip unwanted spaces
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
