'''
Created on Jun 18, 2015

@author: maxim
'''

import asyncio
import os, time, re, psutil, json
from pycontrib.misc.informer import Informer

class Runner(object):
    def __init__(self, stdout=asyncio.subprocess.PIPE, restart_timeout=5, check_timeout=1):
        self.proc = None
        self.stdout = stdout
        self.restart_timeout, self.check_timeout = restart_timeout, check_timeout
        
    def runned(self):
        if self.proc == None:
            return False 
        return self.proc.returncode == None
    
    def genCmd(self):
        raise NotImplementedError('To be implemented')
    
    def needRestart(self):
        raise NotImplementedError('To be implemented')
    
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
        self.cmd, self.outputFn, self.timeout = cmd, outputFn, timeout
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
            return need
        
        r = open(self.outputFn, 'rt')
        m3u8Data = r.read()
        r.close()
        
        indexes = re.findall('#EXT-X-MEDIA-SEQUENCE:(\d+)',m3u8Data)
        if len(indexes):
            self.mediaSequence = int(indexes[0])
        
        i = m3u8Data.find('#EXT-X-ENDLIST')
        if i != -1:
            Informer.info('Trancating #EXT-X-ENDLIST')
            m3u8Data = m3u8Data[:i]
            w = open(self.outputFn, 'wt')
            w.write(m3u8Data)
            w.close()
            
        return need
    
