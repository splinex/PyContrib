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

    def get_argparser(self, additional_args):
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--config", help="configuration file - required")
        argparser.add_argument("--port", help="binding port")
        argparser.add_argument("--debug", help="debug mode")
        argparser.add_argument("--daemon", help="daemon command {start|stop|restart}")
        argparser.add_argument("--log", help="log output")
        for (arg, help) in additional_args:
            argparser.add_argument("--%s" % arg, help=help)
        return argparser

    def initialize(self, config_file=None, config_data=None, redefine_tornado_logging=False, required_args=None):

        self.args = None
        required_args = required_args or []

        if not (config_file or config_data):
            argparser = self.get_argparser(required_args)
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
            if args.log:
                config['GENERAL']['log'] = args.log
            self.daemon = args.daemon
            for (arg, _) in required_args:
                val = args.__getattribute__(arg)
                if not val:
                    raise Exception('Use --help for args')
                self.__setattr__(arg, val)

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

