from pycontrib.misc.informer import Informer
from tornado.ioloop import PeriodicCallback
from datetime import datetime

class NetworkRecorder(object):

    def __init__(self, host, port, callback, **kargs):
        self.host = host
        self.port = port
        self.callback = callback
        self.storePath = kargs.get('storepath', '/tmp')
        self.chunkPeriod = kargs.get('chunkperiod', 600)
        self.bufferSize = int(kargs.get('writebuffersize', 10000000))
        self.bytes = 0
        self.lastActivity = datetime.now()
        self.chunkFn = None
        self.recordInProgress = True
        self.writeBuffer = None
        self._chunk_rotator()
        self.chunk_rotator = PeriodicCallback(self._chunk_rotator, self.chunkPeriod*1000)
        self.chunk_rotator.start()
    
    def _chunk_rotator(self):
        if self.writeBuffer:
            self.writeBuffer.close()
        dateFormat = '{0}-{1}-%Y%m%d-%H%M'.format(self.host, self.port)
        if self.chunkPeriod < 60:
            dateFormat += '%S'                    
        self.chunkFn = '{0}/{1}.ts'.format(self.storePath, datetime.now().strftime(dateFormat))
        self.writeBuffer = open(self.chunkFn, 'wb+', buffering=self.bufferSize)
        Informer.info('Write to {0}'.format(self.chunkFn))        
    
    def on_chunk(self, chunk):
        recvd = len(chunk)
        if recvd == 0:
            return
        self.bytes += recvd
        self.lastActivity = datetime.now()
        if self.callback:
            self.callback(chunk)
        if self.recordInProgress:
            self.writeBuffer.write(chunk)