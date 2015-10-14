'''
Created on Jun 18, 2015

@author: maxim
'''

import asyncio
import subprocess
import os
import time
import re
import psutil
import json
from pycontrib.misc.informer import Informer
from pycontrib.service.monitor import HttpMonitor

class Runner(object):
    def __init__(self, stdout=asyncio.subprocess.PIPE, restart_timeout=5, check_timeout=1):
        self.proc = None
        self.runTime = None
        self.stdout = stdout
        self.restart_timeout, self.check_timeout = restart_timeout, check_timeout
        HttpMonitor.addCallback(self.getState)
        
    def runned(self):
        if self.proc == None:
            return False 
        return self.proc.returncode == None
    
    def genCmd(self):
        raise NotImplementedError('To be implemented')
    
    def needRestart(self):
        raise NotImplementedError('To be implemented')
    
    def getState(self):
        return dict(cmd=self.genCmd(), runned=self.runned(), up_time=(int(time.time()-self.runTime) if self.runTime else None))
    
    @asyncio.coroutine
    def start(self):                 

        while 1: 
            cmd = self.genCmd()                
            cmds = cmd.split()
            if self.runned():
                self.stop()
                yield from asyncio.sleep(self.restart_timeout)
            Informer.info('Run: {0}'.format(cmd))
            self.proc = yield from asyncio.create_subprocess_exec(*cmds, stdout=self.stdout, stderr=asyncio.subprocess.STDOUT)
            self.runTime = time.time()
            while self.runned():
                yield from asyncio.sleep(self.check_timeout)
                if self.needRestart():
                    Informer.error('Need to restart')
                    break      
    
    def stop(self):
        if self.runned():
            self.proc.kill()
    
    def restart(self):
        self.stop()
        self.start()
        
class SimpleRunner(Runner):
    def __init__(self, cmd, logFn=None, outputFn=None, timeout=40):
        if logFn:
            stdout = open(logFn, 'a')
        else:
            stdout = asyncio.subprocess.PIPE
        Runner.__init__(self, stdout)
        self.cmd, self.outputFn, self.timeout, self.logFn = cmd, outputFn, timeout, logFn
        self.targetMDate = 0
        
    def genCmd(self):
        if not self.cmd:
            raise NotImplementedError('To be implemented')
        return self.cmd
    
    def needRestart(self):
        if psutil.virtual_memory().percent > 90:
            Informer.info('Going to restart due to RAM usage')
            Informer.error('Restart due to low mem:\n\n' + json.dumps(list(map(lambda p: (p.name(), p.memory_percent()), psutil.process_iter())), indent=2))
            return True
        
        if not self.outputFn:
            return False
        if self.targetMDate == 0:
            self.targetMDate = time.time()
        elif os.path.exists(self.outputFn):
            self.targetMDate = max(self.targetMDate, os.path.getmtime(self.outputFn))
        restart = (time.time() - self.targetMDate > self.timeout)
        if restart:
            self.targetMDate = 0
            
        return restart
    
class HlsRunner(SimpleRunner):
    
    def __init__(self, *args):
        SimpleRunner.__init__(self, *args)
        self.mediaSequence = 0
        self.needRestart()
    
    def needRestart(self):
        need = SimpleRunner.needRestart(self)
        if not os.path.exists(self.outputFn):
            self.m3u8Data = None
            return need
        
        r = open(self.outputFn, 'rt')
        self.m3u8Data = r.read()
        r.close()
        
        indexes = re.findall('#EXT-X-MEDIA-SEQUENCE:(\d+)', self.m3u8Data)
        if len(indexes):
            self.mediaSequence = int(indexes[0])
        
        i = self.m3u8Data.find('#EXT-X-ENDLIST')
        if i != -1:
            Informer.info('Trancating #EXT-X-ENDLIST')
            self.m3u8Data =self.m3u8Data[:i]
            w = open(self.outputFn, 'wt')
            w.write(self.m3u8Data)
            w.close()
            
        return need
    
    def getState(self):
        state = SimpleRunner.getState(self)
        state['misc'] = self.m3u8Data
        if self.logFn:
            try:
                state['log'] = subprocess.check_output(['tail', '-30', self.logFn]).decode()
            except Exception as e:
                state['log'] = repr(e)
        return state
