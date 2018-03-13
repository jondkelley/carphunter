#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# Written by Jonathan Kelley, March 7, 2018
# March 12, Added config support from yaml..

# pip2.7 install unidecode
# pip2.7 install loadconfig
# pip2.7 install netmiko
# pip2.7 install --upgrade paramiko
# pip2.7 install cryptography
# pip2.7 uninstall gssapi
# pip2.7 install yamlcfg
# pip2.7 install prettytable
# pip2.7 install configloader

# pip3.4 install netmiko
# pip3.4 install unidecode
# pip3.4 install cryptography
# pip3.4 install yamlcfg
# pip3.4 install prettytable
# pip3.4 install loadconfig
import sys
from unidecode import unidecode
import json
from pprint import pprint
import argparse

from carpconf import ConfigHelper
from itemsearch import (search_arp_table, ip2arp, print_table)
from poller import (a_device, poll_devices)
from cache import (DateTimeEncoder, Cache)

parser = argparse.ArgumentParser(description="Cisco Arp Hunter v0.1",
                                 epilog=("This Python based tool uses Net"
                                         "miko to search your Cisco® bran"
                                         "ded routers and switches. This "
                                         "tool creates an ARP cache in a "
                                         "local json file (using --poll)."
                                         " --mac and -ip can be used to f"
                                         "ind MAC, IP, PORT and VLAN asso"
                                         "ciations immediately against th"
                                         "is json cache."
                                         ))
parser.add_argument('-m', '--mac', action="store", dest="mac",
                    help="Search json cache for MAC to port/vlan mappings")
parser.add_argument('-i', '--ip', action="store", dest="ip",
                    help="Search json cache for IP address to MAC mapping")
parser.add_argument('--poll', action="store_true", default=False,
                    dest="pollmode", help=("Poll devices now and save "
                                           "to local json-cache-file"))
parser.add_argument('--json', action="store_true", default=False,
                    dest="json", help="Print output in JSON format")
parser.add_argument('--all-ports', action="store_true", default=False,
                    dest="allports", help=("List all ports in cache "
                                           "search including port channels"))
parser.add_argument('--config', action="store", default="/etc/carphunter.yml",
                    dest="configfile", help="Non-default config file location")
parser.add_argument('--json-cache-file', action="store", default="/mnt/data/arp.json",
                    dest="cachedbfile", help="Non-default json-cache-file location")
args = parser.parse_args()

conf = ConfigHelper(path=args.configfile)

print(vars(args))

def print_json(dictionary):
    """
    print json text in clear readworthy format
    """
    return(json.dumps(dictionary,
                     indent=2,
                     default=str)
          )


def user_confirm(message=None, default_return=False):
    """
    asks the user y or n, then returns a true/false for processing
    arguement message (string): optional message to print before asking
    arguement default_return (bool): optional default if return pressed
    """
    if message:
        sys.stdout.write(message)
    sys.stdout.write("   Type 'yes' or 'no': ")
    # python3 choice = input().lower()
    choice = raw_input().lower()
    if "y" in choice:
        return True
    elif "n" in choice:
        return False
    elif "" in choice:
        return default_return
    else:
        return None


lol = True

def main():
    # arg parse
    if len(sys.argv) == 1:
        choice = user_confirm(message=("WARNING : No arguements will display "
                                       "ALL NETWORK DATA, are you sure?\n"))
        print(choice)
        if choice:
            pass
        elif choice == False:
            print("Exiting...")
            exit(1)

    if args.pollmode:
        # --poll flag
        print(("Collection polling started. Do not"
               " terminate or data will not be saved."))
        poll_devices()
    else:
        # not --poll flag
        if args.ip:
            # --ip flag
            ip2arp(args)
        else:
            # --mac flag
            if not args.mac:
                args.mac = "."
            search_arp_table(args)

if "__main__" == __name__:
    main()
