#!/usr/bin/env python
# -*- coding: utf-8 -*-

from loadconfig import Config


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
