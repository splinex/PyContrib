'''
Created on Jun 18, 2015

@author: maxim
'''
import logging
import argparse
import configparser

from pycontrib.misc.informer import Informer
from pycontrib.misc.patterns import Singleton

class Environment(Singleton):
    '''
    Environment configuration
    '''
    def initialize(self, config_file=None, config_data=None):
        
        if not (config_file or config_data):
            argparser = argparse.ArgumentParser()
            argparser.add_argument("--config", help="configuration file - required")
            argparser.add_argument("--port", help="binding port")
            argparser.add_argument("--debug", help="debug mode")
    
            args = argparser.parse_args()
    
            if not args.config:
                raise Exception('Use --help for args')
            
            config_file = args.config
        else:
            args = None
        self.configFn = config_file
            
        config = configparser.ConfigParser()
        config.optionxform = str
        
        if config_file:
            config.read(config_file)
        else:
            config.read_string(config_data)

        if not args is None:
            if args.port:
                config['NETWORK']['port'] = args.port
            if args.debug:
                config['GENERAL']['debug'] = 'True'

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

        Informer.initEnv(self)

        Informer.info('{0} started at {1}:{2}'.format(self.name, self.host, self.port))
