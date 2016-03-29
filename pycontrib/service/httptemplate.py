'''
Created on Jul 15, 2015

@author: maxim
'''
import tornado.template
from pycontrib.service.login import LoginRequestHandler
from pycontrib.misc.informer import Informer

class HttpTemplateRequestHandler(LoginRequestHandler):
    
    meta = None
    _indext = None
    
    def initialize(self, env):
        LoginRequestHandler.initialize(self)
        self.env = env
        cls = type(self)
        if cls._indext == None:
            if not cls.meta:
                raise NotImplementedError('Meta should be defined')
            try:
                templatedir = env.config['HTML']['templatedir']
                if templatedir[0] != '/':
                    templatedir = '{0}/{1}'.format(env.home, templatedir)
                loader = pycontrib.tornado.template.Loader(templatedir)
                cls._indext = loader.load(cls.meta['template'])
            except Exception as e:
                Informer.error('can not load templates! {0}'.format(e))
                cls._indext = None
