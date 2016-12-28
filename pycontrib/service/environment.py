'''
Created on Jun 18, 2015

@author: maxim
'''
import argparse
import configparser
import logging

from pycontrib.misc.informer import Informer
from pycontrib.misc.patterns import Singleton


class Environment(Singleton):
    '''
    Environment configuration
    '''

    def get_argparser(self):
        argparser = argparse.ArgumentParser()
        argparser.add_argument('--config', help="configuration file - required")
        argparser.add_argument('--port', help="binding port")
        argparser.add_argument('--debug', help="debug mode")
        argparser.add_argument('--daemon', help="daemon command {start|stop|restart}")
        argparser.add_argument('--command', help='maintenance command, ex db.clear')
        return argparser

    def initialize(self, config_file=None, config_data=None, redefine_tornado_logging=False):

        self.args = None

        if not (config_file or config_data):
            argparser = self.get_argparser()
            args = argparser.parse_args()

            if not args.config:
                raise Exception('Use --help for args')

            config_file = args.config
        else:
            args = None
        self.configFn = config_file

        self.args = args

        config = configparser.ConfigParser()
        config.optionxform = str

        if config_file:
            config.read(config_file)
        else:
            config.read_string(config_data)

        if args is not None:
            if args.port:
                config['NETWORK']['port'] = args.port
            if args.debug:
                config['GENERAL']['debug'] = 'True'
            self.daemon = args.daemon
            self.command = args.command

        if 'LOGIN' in config:
            cl = config['LOGIN']
            login = {'admins': {cl['adminlogin']: cl['adminpass']}, 'users': {cl['userlogin']: cl['userpass']}}
        else:
            login = None

        network = config['NETWORK']
        general = config['GENERAL']

        self.login = login
        self.host = network.get('host', '127.0.0.1')
        self.port = int(network.get('port', '80'))
        self.name = general.get('name', 'service')
        self.debug = (general.get('debug', 'False') == 'True')
        self.home = general.get('home', '')
        self.log = general.get('log', '{0}/{1}.log'.format(self.home, self.name))

        self.config = config

        Informer.initEnv(self, redefine_tornado_logging=redefine_tornado_logging)

        Informer.info('{0} started at {1}:{2}'.format(self.name, self.host, self.port))
