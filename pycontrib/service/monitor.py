'''
Created on Jul 7, 2015

@author: maxim
'''

import tornado.web, tornado.gen
import json
import psutil

class HttpMonitor(tornado.web.RequestHandler):
    
    _callbacks = []
    
    def initialize(self, env, defaults):
        self.env = env
        self.defaults = defaults
    
    @classmethod
    def addCallback(cls, callback):
        cls._callbacks.append(callback)
        
    @tornado.gen.coroutine
    def get(self, *args):
        ans = {}
        ans.update(self.defaults)
        ans.update(dict(name = self.env.name,
                   host=self.env.host, 
                   ram=psutil.virtual_memory().percent,
                   cpu=psutil.cpu_percent(),
                   sent=psutil.net_io_counters().bytes_sent,
                   recv=psutil.net_io_counters().bytes_recv,
                   disk_usage=list(map(lambda p: (p.mountpoint, psutil.disk_usage(p.mountpoint).percent), psutil.disk_partitions())),
                   states=[],
                   issues=[]))
        
        if ans['ram'] > 90:
            ans['issues'].append('High RAM usage')
        if ans['cpu'] > 90:
            ans['issues'].append('High CPU usage')
        for du in ans['disk_usage']:
            if du[1] > 90:
                ans['issues'].append('High HDD usage at '+du[0])
        
        for callback in HttpMonitor._callbacks:
            ans['states'].append(callback())
            
        self.set_status(200)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Expose-Headers', 'Access-Control-Allow-Origin')
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ans, indent=2))
        self.finish()
        