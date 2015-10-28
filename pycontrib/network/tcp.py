import tornado.gen
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.tcpclient import TCPClient
from tornado.tcpserver import TCPServer

from collections import namedtuple
from functools import partial
import datetime
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

    @property
    def state(self):
        if self._state == CONNECTION_STATE.CONNECTED and not self.alive():
            self._state = CONNECTION_STATE.CHECKFAILS
        return self._state
    
    @reporting_coroutine
    @tornado.gen.coroutine
    def _connect(self):        
        if self.state in (CONNECTION_STATE.CONNECTING, CONNECTION_STATE.CONNECTED): 
            return
        
        if self.state == CONNECTION_STATE.CHECKFAILS:
            self.disconnect()
            
        Informer.info('Connecting to target at tcp://{0}:{1}'.format(self.host, self.port))     
        self._state = CONNECTION_STATE.CONNECTING
        yield tornado.gen.Task(IOLoop.current().add_timeout, datetime.timedelta(seconds=randint(1,10)))
        try:
            #TODO: patch library in contrib
            self.stream = yield TCPClient.connect(self, self.host, self.port) #, max_write_buffer_size=5000000)
        except Exception as e:
            Informer.info(e)
            self.disconnect()                      
            return
    
        self.stream.set_close_callback(self._on_close)
        self._state = CONNECTION_STATE.CONNECTED
        Informer.info('Connected to target at tcp://{0}:{1}'.format(self.host, self.port))
        self.on_connect()
        
    def connect(self):
        self.connection_rotator = PeriodicCallback(partial(ReconnectableTCPClient._connect, self), 5000)
        self.connection_rotator.start()
        
    def disconnect(self):
        Informer.info('Disconnecting from target at tcp://{0}:{1}'.format(self.host, self.port))
        self._state = CONNECTION_STATE.DISCONNECTED
        if self.stream and not self.stream.closed(): 
            self.stream.close()
        
    def _on_close(self, *args, **kwargs):
        self._state = CONNECTION_STATE.DISCONNECTED
        self.on_close()
        
    def on_connect(self):
        pass
        
    def on_close(self, *args, **kwargs):
        pass
    
    def alive(self):
        return True
    
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
    