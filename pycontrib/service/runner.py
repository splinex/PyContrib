'''
Created on Jun 18, 2015

@author: maxim
'''

import asyncio
import logging, os, time

class Runner(object):
    def __init__(self, stdout=asyncio.subprocess.PIPE, restart_timeout=5, check_timeout=2):
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
        cmd = self.genCmd()                
        cmds = cmd.split()
        while 1: 
            if self.runned():
                self.stop()
                yield from asyncio.sleep(self.restart_timeout)
            logging.info('Run: {0}'.format(cmd))
            self.proc = yield from asyncio.create_subprocess_exec(*cmds, stdout=self.stdout, stderr=asyncio.subprocess.STDOUT)
            while self.runned():
                yield from asyncio.sleep(self.check_timeout)
                if self.needRestart():
                    logging.info('Going to restart command')
                    break      
    
    def stop(self):
        if self.runned():
            self.proc.kill()
    
    def restart(self):
        self.stop()
        self.start()
        
class SimpleRunner(Runner):
    def __init__(self, cmd, stdout=asyncio.subprocess.PIPE, outputFn=None, timeout=40):        
        Runner.__init__(self, stdout)
        self.stdout = stdout
        self.cmd, self.outputFn, self.timeout = cmd, outputFn, timeout
        self.targetMDate = 0
        
    def genCmd(self):
        if not self.cmd:
            raise NotImplementedError('To be implemented')
        return self.cmd
    
    def needRestart(self):
        if not self.outputFn:
            return False
        if os.path.exists(self.outputFn):
            self.targetMDate = os.path.getmtime(self.outputFn)
        elif self.targetMDate == 0:
            self.targetMDate = time.time()
        restart = (time.time() - self.targetMDate > self.timeout)
        if restart:
            self.targetMDate = 0
        return restart
    