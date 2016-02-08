'''
Created on Jun 18, 2015

@author: maxim
'''

import argparse, configparser, logging
from pycontrib.misc.informer import Informer

class _Environment(object):

    def __init__(self, config):
        self.config = config

        self.host = self.config['NETWORK'].get('host', '127.0.0.1')
        self.port = int(self.config['NETWORK'].get('port', '0'))
        self.name = self.config['GENERAL'].get('name', 'service')
        self.debug = (self.config['GENERAL'].get('debug', 'False') == 'True')
        self.home = self.config['GENERAL'].get('home', '')
        self.log = self.config['GENERAL'].get('log', '{0}/{1}.log'.format(self.home, self.name))

        if 'LOGIN' in self.config:
            cl = self.config['LOGIN']
            self.login = {'admins': {cl['adminlogin']: cl['adminpass']}, 'users': {cl['userlogin']: cl['userpass']}}

        Informer.initEnv(self)

        Informer.info('{0} started at {1}:{2}'.format(self.name, self.host, self.port))

    @classmethod
    def from_file(cls, config_file):
        if not config_file:
            return None

        config = cls.__parse_config(config_file)
        return cls(config)

    @classmethod
    def from_args(cls):
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--config", help="configuration file - required")
        argparser.add_argument("--port", help="binding port")
        argparser.add_argument("--debug", help="debug mode")
        args = argparser.parse_args()
        if args.config:
            configFn = args.config
        else:
            raise BaseException('Use --help for args')

        config = cls.__parse_config(configFn)

        if args.port:
            config['NETWORK']['port'] = args.port
        if args.debug:
            config['GENERAL']['debug'] = 'True'

        return cls(config)

    @staticmethod
    def __parse_config(configFn):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(configFn)

        return config


def Environment(config_file=None):
    return _Environment.from_file(config_file) or _Environment.from_args()
