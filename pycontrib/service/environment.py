'''
Created on Jun 18, 2015

@author: maxim
'''

import argparse, configparser, logging

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
        
        if args.port:
            self.config['NETWORK']['port'] = args.port
        if args.debug:
            self.config['GENERAL']['debug'] = 'True'
        
        try:
            self.port = self.config['NETWORK']['port']
            self.name = self.config['GENERAL']['name']
            self.debug = (self.config['GENERAL']['debug'] == 'True')
            self.home = self.config['GENERAL']['home']
        except Exception as e:
            raise BaseException('Config file is not valid: {0}'.format(e))
        
        logging.basicConfig(filename='{0}/{1}.log'.format(self.home, self.name), 
                            level=(logging.DEBUG if self.debug else logging.info), 
                            format='{0}:{1}:%(levelname)s:%(asctime)s: %(message)s'.format(self.name, self.port))
        
        logging.info('{0} started at {1}'.format(self.name, self.port))
