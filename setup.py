#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup

sys.path.insert(0, '.')

if __name__ == "__main__":
    package = "carphunter"
    setup(
        name=package,
        version="0.1",
        author="Jonathan Kelley",
        author_email="jonkelley@gmail.com",
        url="https://github.com/jondkelley/carphunter",
        license="BSD License",
        packages=[package],
        package_dir={package: package},
        description=(
            'This Python based tool uses Netmiko to search your Cisco® branded routers'
            ' and switches.'
        ),
        long_description=(
            'This Python based tool uses Netmiko to search your Cisco® branded routers'
            ' and switches. This tool creates an ARP cache in a local json file (using'
            ' --poll). --mac and -ip can be used to find MAC, IP, PORT and VLAN associ'
            'ations immediately against this json cache.'
        ),
        classifiers=[
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: System :: Monitoring',
            'Topic :: System :: Networking',
            'Topic :: System :: Systems Administration ',
            'Topic :: Utilities',
            'Topic :: Internet',
            'Topic :: Communications'
        ],
        entry_points={
            'console_scripts': ['carphunter = carphunter.main:main'],
        },
        data_files=[('/etc', ['carphunter.yml'])],
        install_requires=[
            'netmiko',
            'paramiko',
            'cryptography',
            'unidecode',
            'prettytable',
            'loadconfig',
            'argparse',
            'pytest'
        ]
    )

