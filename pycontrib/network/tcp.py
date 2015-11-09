import tornado.gen
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.tcpclient import TCPClient
from tornado.tcpserver import TCPServer

from collections import namedtuple
from functools import partial
from datetime import datetime
from random import randint
from abc import ABCMeta, abstractmethod

from pycontrib.misc.coroutine import reporting_coroutine, unfailable_coroutine
from pycontrib.misc.informer import Informer

CONNECTION_STATE = namedtuple('ConnectionStateCls', ['DISCONNECTED', 'CONNECTING', 'CONNECTED', 'CHECKFAILS'])(*range(4))

class ReconnectableTCP(metaclass=ABCMeta):

    def __init__(self, host, port):
        self.stream = None
        self.host = host
        self.port = port
        self._state = CONNECTION_STATE.DISCONNECTED

    @abstractmethod
    def alive(self):
        return True

    @property
    def state(self):
        if self._state == CONNECTION_STATE.CONNECTED and not self.alive():
            self._state = CONNECTION_STATE.CHECKFAILS
        return self._state

class ReconnectableTCPClient(TCPClient):
        
    def __init__(self, host, port):
        TCPClient.__init__(self)
        self.stream = None
        self.host = host
        self.port = port
        self._state = CONNECTION_STATE.DISCONNECTED
        self.lastActivity = datetime.now()
        self.tcpTimeout = 60
        self.fullBuffer = False
        self.upStreamInProgress = True
        
        self.band_rotator = PeriodicCallback(partial(ReconnectableTCPClient._band, self), 1000)
        self.band_rotator.start()
        
        self.inBytes = 0
        self.outBytes = 0
        self.droppedBytes = 0
        self.inBytesPrev, self.outBytesPrev, self.droppedBytesPrev = self.inBytes, self.outBytes, self.droppedBytes
        self.inBand = 0
        self.outBand = 0
        self.droppedBand = 0
        self.bandHistory = [(0,0,0),]*300 
        self.connection_rotator = PeriodicCallback(partial(ReconnectableTCPClient._connect, self), 5000+randint(0,2000))
        self.connection_rotator.start()
        

    @reporting_coroutine
    @tornado.gen.coroutine
    def _band(self):
        self.inBand = (self.inBytes - self.inBytesPrev) // 1024
        self.outBand = (self.outBytes - self.outBytesPrev) // 1024
        self.droppedBand = (self.droppedBytes - self.droppedBytesPrev) // 1024
        self.inBytes, self.outBytes, self.droppedBytes = self.inBytes, self.outBytes, self.droppedBytes % (1024**4)
        self.inBytesPrev, self.outBytesPrev, self.droppedBytesPrev = self.inBytes, self.outBytes, self.droppedBytes
        self.bandHistory = self.bandHistory[1:] + [(self.inBand, self.outBand, self.droppedBand)]
        
    @reporting_coroutine
    @tornado.gen.coroutine
    def _connect(self):
        
        if self.state in (CONNECTION_STATE.CONNECTING, CONNECTION_STATE.CONNECTED): 
            return
        
        if self.state == CONNECTION_STATE.CHECKFAILS:
            self.disconnect()
            
        Informer.info('Connecting to target at tcp://{0}:{1}'.format(self.host, self.port))     
        self._state = CONNECTION_STATE.CONNECTING
        try:
            #TODO: patch library in contrib
            self.stream = yield TCPClient.connect(self, self.host, self.port) #, max_write_buffer_size=5000000)
        except Exception as e:
            Informer.info(e)
            self.reconnect()
            return
    
        self.stream.set_close_callback(self._on_close)
        self._state = CONNECTION_STATE.CONNECTED
        Informer.info('Connected to target at tcp://{0}:{1}'.format(self.host, self.port))
        self._on_connect()
        
    @reporting_coroutine
    @tornado.gen.coroutine
    def _on_connect(self):
        while 1:
            try:
                chunk = yield self.stream.read_bytes(10000000, partial=True)
            except:
                self.disconnect()
                return
            self.inBytes += len(chunk)
            self.on_chunk(chunk)
            self.lastActivity = datetime.now()
            
    def on_chunk(self, chunk):
        pass
    
    @reporting_coroutine
    @tornado.gen.coroutine
    def write(self, chunk):
        chunkLen = len(chunk)
        if self.state != CONNECTION_STATE.CONNECTED:
            self.droppedBytes += chunkLen
            return
        elif self.fullBuffer and self.stream.writing():
            self.droppedBytes += chunkLen
            return
            
        self.fullBuffer = False
        if self.upStreamInProgress:
            try:
                yield self.stream.write(chunk)
                self.lastActivity = datetime.now()            
            except tornado.iostream.StreamClosedError as e:
                Informer.info(e)
                self.disconnect()
            except tornado.iostream.StreamBufferFullError as e:
                self.fullBuffer = True
                Informer.info(e)
            except Exception as e:
                Informer.info(e)
            else:
                self.outBytes += chunkLen
        else:
            self.lastActivity = datetime.now()

    def reconnect(self):
        Informer.info('Disconnecting from target at tcp://{0}:{1}'.format(self.host, self.port))
        self._state = CONNECTION_STATE.DISCONNECTED
        if self.stream and not self.stream.closed(): 
            self.stream.close()
        
    def _on_close(self, *args, **kwargs):
        self._state = CONNECTION_STATE.DISCONNECTED
                
    def alive(self):
        return (datetime.now()-self.lastActivity).seconds < self.tcpTimeout
    
    @property
    def state(self):
        if self._state == CONNECTION_STATE.CONNECTED and not self.alive():
            self._state = CONNECTION_STATE.CHECKFAILS
        return self._state
    
    def __del__(self):
        self.reconnect()
        self.connection_rotator.stop()
        self.band_rotator.stop()
        
class InServer(TCPServer):
    
    def __init__(self, env):
        TCPServer.__init__(self)             
        self.env = env
        self.storeStream = eval(env.get('storestream', 'False'))
        self.connected = False
        self.bufferSize = int(env.get('writebuffersize', '10000000'))
        self.chunkPeriod = int(env.get('chunkperiod', '60'))
        self.storePath = env.get('storepath', '/tmp')
        self.stream_callback = None
        self.writeBuffer = None
        self.trafficIn = 0
        self.stream = None
    
    @reporting_coroutine
    @tornado.gen.coroutine
    def chunk_rotator(self):        
        while 1:
            dateFormat = '%Y%m%d-%H%M'
            if self.chunkPeriod < 60:
                dateFormat += '%S'
                
            chunkFn = '{0}/{1}.ts'.format(self.storePath, datetime.now().strftime(dateFormat))
            self.writeBuffer = open(chunkFn, 'wb+', buffering=self.bufferSize)
            yield tornado.gen.sleep(self.chunkPeriod)
            self.writeBuffer.close()
            
    def start(self, num_processes=1):
        TCPServer.start(self, 1)
        if self.storeStream:
            self.chunk_rotator()

    def set_stream_callback(self, stream_callback):
        self.stream_callback = stream_callback

    @reporting_coroutine
    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        if self.connected:                
            stream.close()
            Informer.info('Just one camera allowed')
            return
        self.connected = True
        assert(self.stream_callback)
        
        self.stream = stream
        while not self.stream.closed():
            try:
                chunk = yield stream.read_bytes(188*1000, partial=True)
                self.trafficIn += len(chunk)
                self.stream_callback(chunk)
            except:
                pass
            else:
                if self.writeBuffer:
                    self.writeBuffer.write(chunk)
        self.connected = False
            
    def traffic(self):
        traffic = self.trafficIn
        self.trafficIn = 0
        return traffic
    