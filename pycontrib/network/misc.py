class NetworkRecorder(object):
    '''
    base class for network connectors
    '''
    
    def __init__(self, host, port, callback, **kargs):
        self.host = host
        self.port = port
        self.callback = callback
        self.storePath = kargs.get('storepath', '/tmp')
        self.chunkPeriod = kargs.get('chunkperiod', 600)
        self.storeStream = eval(kargs.get('storestream', 'True'))
        self.bufferSize = int(kargs.get('writebuffersize', 10000000))
        self.bytes = 0
        self.lastActivity = datetime.now()
        self.chunkFn = None
        if self.storeStream:
            self.writeBuffer = None
            self._chunk_rotator()
            self.chunk_rotator = PeriodicCallback(self._chunk_rotator, self.chunkPeriod*1000)
            self.chunk_rotator.start()
            
    def start_record(self):
        self.recordInProgress = True
        
    def stop_record(self):
        self.recordInProgress = False
    
    def _chunk_rotator(self):
        if self.writeBuffer:
            self.writeBuffer.close()
        dateFormat = '{0}-{1}-%Y%m%d-%H%M'.format(self.host, self.port)
        if self.chunkPeriod < 60:
            dateFormat += '%S'                    
        self.chunkFn = '{0}/{1}.ts'.format(self.storePath, datetime.now().strftime(dateFormat))
        self.writeBuffer = open(self.chunkFn, 'wb+', buffering=self.bufferSize)
        Informer.info('Write to {0}'.format(self.chunkFn))        
    
    def chunk_recieved(self, chunk):
        recvd = len(chunk)
        if recvd == 0:
            return
        self.bytes += recvd
        self.lastActivity = datetime.now()
        if self.callback:
            self.callback(chunk)
        if self.storeStream:
            self.writeBuffer.write(chunk)