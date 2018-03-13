# carphunter

Carphunter is a Python-based network management tool that uses Netmiko to search your Cisco® branded routing/switching equipment. This tool is used to quickly examine recent IP, ARP, and VLAN associations across the  network.

## Setup

#### 1) Install the software

The latest release is in pip:


     pip install carphunter

You can always run the latest release from this repository by:

     python setup.py install

#### 2) Make scheduled cron

A cron job allows the tool to automatically keep the database up to date based on your own schedule. On most systems you can edit ```/etc/crontab``` and add

    */10 * * * * root /bin/carphunter --poll

This will save the networks arp database to /etc/carphunter.json every 10 minutes.

#### 3) Edit configuration for your network

TODO

#### 4) Create initial database

This will test connectivity to your network build an initial database.

    carphunter --poll
   

## How it works

This tool uses json and Netmiko to poll all of your existing devices and stores a small database of items. This can be searched using the parameters --mac and --ip to display items in this json database.

## Command Examples

### Find all ARP entries for ```001c.c46b.beef```

This command will check every switch and router for any ARP or MAC table related entries containing a MAC address. Partial matches are supported.

    carphunter -m 001c.c46b.beef

Sample output:

    Checking network for `001c.c46b.beef`...

    Routing Device: TX-DFW-6509-01 found match!
    +----------------+-----------------+------+-----+-------+
    |     hwaddr     |        ip       | vlan | age | proto |
    +----------------+-----------------+------+-----+-------+
    | 001c.c46b.beef | 10.10.1.29      | N/A  |  -  |  ARPA |
    | 001c.c46b.beef |  10.10.1.30     | N/A  |  -  |  ARPA |
    | 001c.c46b.beef |  10.10.1.31     | N/A  |  -  |  ARPA |
    | 001c.c46b.beef |  10.10.1.32     | N/A  |  -  |  ARPA |
    +----------------+-----------------+------+-----+-------+

    Switching Device: TX-DFW-RACK-A12 found match!
    +----------------+-----------+------+--------+
    |     hwaddr     | interface | vlan |  mode  |
    +----------------+-----------+------+--------+
    | 001c.c46b.beef |   Gi0/20  |  30  | STATIC |
    +----------------+-----------+------+--------+

    Statistics:
      * Cache contains 1 routers, 23 switches
      * Cache updated 2018-03-13T15:47:16.069718
      * Last poller took 0:02:14.006661
      * This lookup took 0:00:00.031692


### Find IP for ```10.10.1.100```

This command will return IP, MAC, VLAN, AGE and ENCAPSULATION PROTOCOL. Partial matches are supported.

    carphunter -i  10.10.1.100
 
 Sample output:
 
    Checking network for `10.10.1.100` ARPA entry...

    Routing Device: TX-GVO-DC-6509-01 found a matching IP!
    +---------------+----------------+------+-----+-------+
    |       ip      |     hwaddr     | vlan | age | proto |
    +---------------+----------------+------+-----+-------+
    |  10.10.1.100  | 001c.c46b.a0fe |  1   |  3  |  ARPA |
    +---------------+----------------+------+-----+-------+

### Find IP using partial match ```10.10.1```

    carphunter -i  10.10.1
 
 Sample output (ambiguous matches):
 
    Checking network for `10.10.1` ARPA entry...

    Routing Device: TX-GVO-DC-6509-01 found a matching IP!
    +---------------+----------------+------+-----+-------+
    |       ip      |     hwaddr     | vlan | age | proto |
    +---------------+----------------+------+-----+-------+
    |  10.10.1.100  | 5a1f.fa30.1111 |  1   |  3  |  ARPA |
    |  10.10.1.101  | 0022.1968.0c11 |  1   |  1  |  ARPA |
    |  10.10.1.102  | 5a1f.ff30.111e |  1   |  2  |  ARPA |
    +---------------+----------------+------+-----+-------+

