'''
Created on Jun 18, 2015

@author: maxim
'''

import argparse, configparser, logging
from pycontrib.misc.informer import Informer

class Environment(object):
    
    def __init__(self):
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--config", help="configuration file - required")
        argparser.add_argument("--port", help="binding port")
        argparser.add_argument("--debug", help="debug mode")
        args = argparser.parse_args()
        if args.config:
            configFn = args.config
        else:
            raise BaseException('Use --help for args')     
           
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.read(configFn)
        
        self.configFn = configFn
        
        if args.port:
            self.config['NETWORK']['port'] = args.port
        if args.debug:
            self.config['GENERAL']['debug'] = 'True'
        
        try:
            self.host = self.config['NETWORK'].get('host', '127.0.0.1')
            self.port = int(self.config['NETWORK'].get('port', '0'))
            self.name = self.config['GENERAL'].get('name', 'service')
            self.debug = (self.config['GENERAL'].get('debug', 'False') == 'True')
            self.home = self.config['GENERAL'].get('home', '')
            self.log = self.config['GENERAL'].get('log', '{0}/{1}.log'.format(self.home, self.name))
        except Exception as e:
            raise BaseException('Config file is not valid: {0}'.format(e))
        
        
        if 'LOGIN' in self.config:
            cl = self.config['LOGIN']
            self.login = {'admins': {cl['adminlogin']: cl['adminpass']}, 'users': {cl['userlogin']: cl['userpass']}}
        
        Informer.initEnv(self)
        
        Informer.info('{0} started at {1}:{2}'.format(self.name, self.host, self.port))
        