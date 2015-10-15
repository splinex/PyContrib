'''
Created on Jul 7, 2015

@author: maxim
'''

import tornado.web, tornado.gen
import json
import psutil

class HttpMonitor(tornado.web.RequestHandler):
    
    _callbacks = []
    
    def initialize(self, env):
        self.env = env
    
    @classmethod
    def addCallback(cls, callback):
        cls._callbacks.append(callback)
        
    @tornado.gen.coroutine
    def get(self, *args):
        ans = dict(name = self.env.name,
                   host=self.env.host, 
                   ram=psutil.virtual_memory().percent,
                   cpu=psutil.cpu_percent(),
                   sent=psutil.net_io_counters().bytes_sent,
                   recv=psutil.net_io_counters().bytes_recv,
                   disk_usage=list(map(lambda p: (p.mountpoint, psutil.disk_usage(p.mountpoint).percent), psutil.disk_partitions())),
                   states=[])
        
        for callback in HttpMonitor._callbacks:
            ans['states'].append(callback())
            
        self.set_status(200)
        self.write(json.dumps(ans, indent=2))
        self.finish()
        