'''
Created on Jul 15, 2015

@author: maxim
'''
import tornado.web, tornado.template
from pycontrib.service.login import LoginRequestHandler

class HttpTemplateRequestHandler(LoginRequestHandler):
    
    meta = None
    _indext = None
    
    def initialize(self, env):
        LoginRequestHandler.initialize(self)
        self.env = env
        cls = type(self)
        if cls._indext == None:
            if not cls.meta:
                raise NotImplementedError('meta should be defined')            
            try:
                loader = tornado.template.Loader('{0}'.format(env.config['HTML']['templatedir']))
                cls._indext = loader.load(cls.meta['template'])
            except Exception as e:
                print('can not load templates! {0}'.format(e))
                cls._indext = None