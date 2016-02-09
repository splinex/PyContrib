'''
Created on Jun 18, 2015

@author: maxim
'''
import logging
import argparse
import configparser

from pycontrib.misc.informer import Informer


class _Environment:
    def __init__(self, config):
        if 'LOGIN' in config:
            cl = config['LOGIN']
            login = {'admins': {cl['adminlogin']: cl['adminpass']}, 'users': {cl['userlogin']: cl['userpass']}}
        else:
            login = None

        network = config['NETWORK']
        general = config['GENERAL']

        self.login = login
        self.host = network.get('host', '127.0.0.1')
        self.port = int(network.get('port', '0'))
        self.name = general.get('name', 'service')
        self.debug = (general.get('debug', 'False') == 'True')
        self.home = general.get('home', '')
        self.log = general.get('log', '{0}/{1}.log'.format(self.home, self.name))

        self.config = config

        Informer.initEnv(self)

        Informer.info('{0} started at {1}:{2}'.format(self.name, self.host, self.port))

    @classmethod
    def from_file(cls, config_file):
        if not config_file:
            return None

        config = cls._parse_config_ini(config_file)
        return cls(config)

    @classmethod
    def from_args(cls):
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--config", help="configuration file - required")
        argparser.add_argument("--port", help="binding port")
        argparser.add_argument("--debug", help="debug mode")

        args = argparser.parse_args()

        if not args.config:
            raise Exception('Use --help for args')

        config = cls._parse_config_ini(args.config)

        if args.port:
            config['NETWORK']['port'] = args.port
        if args.debug:
            config['GENERAL']['debug'] = 'True'

        return cls(config)

    @staticmethod
    def _parse_config_ini(file_name):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(file_name)

        return config


def Environment(config_file=None):
    return _Environment.from_file(config_file) or _Environment.from_args()
