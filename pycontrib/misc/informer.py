import smtplib, logging, asyncio

class Mailer(object):
    _smtpServer = None
    _smtpHost = None
    _toAddr = None
    _fromAddr = None
    _password = None
    _prevMsg = None
    _name = None
        
    @classmethod
    def initCredentials(cls, name, smtphost=None, fromaddr=None, toaddr=None, password=None, prefix=None):
        if None in (name, smtphost, fromaddr, toaddr, password):
            return
        if Mailer._smtpServer:
            Mailer.disconnect()
        Mailer._name = name
        Mailer._fromAddr = fromaddr      
        Mailer._toAddr = toaddr      
        Mailer._password = password
        Mailer._smtpHost = smtphost
        Mailer._prefix = prefix
            
    @classmethod
    def connect(cls):
        try:
            Mailer._smtpServer = smtplib.SMTP(Mailer._smtpHost)
            Mailer._smtpServer.starttls()
            Mailer._smtpServer.login(Mailer._fromAddr, Mailer._password)
        except Exception as e:
            logging.error(e)
            Mailer._smtpServer = None        
    
    @classmethod    
    def disconnect(cls):
        try:
            Mailer._smtpServer.quit()
        except Exception as e:
            logging.error(e)
            Mailer._smtpServer = None
        
    @classmethod
    def send(cls, msg):
        if msg == Mailer._prevMsg:
            return
        if not Mailer._smtpHost:
            logging.error('Mailer was not inited')
            return
        Mailer.connect()
        try:
            Mailer._smtpServer.sendmail(Mailer._fromAddr, 
                                        (Mailer._toAddr,), 
                                        "From: %s\r\nTo: %s\r\nSubject: Message from %s (%s)\r\n\r\n%s\r\n\r\n" % (Mailer._fromAddr, Mailer._toAddr, Mailer._name, Mailer._prefix, msg))
        except Exception as e:
            logging.error(e)
            Mailer._smtpServer = None
        else:
            Mailer._prevMsg = msg
            Mailer.disconnect() 

class Informer(object):
    
    @classmethod
    def initEnv(cls, env):
        logging.basicConfig(filename='{0}/{1}.log'.format(env.home, env.name),
                            level=(logging.DEBUG if env.debug else logging.CRITICAL),
                            format='{0}:{1}:%(levelname)s:%(asctime)s: %(message)s'.format(env.name, env.port))

        Mailer.initCredentials(env.name, env.config['MAILING']['smtpserver'], env.config['MAILING']['fromaddr'], 
                                      env.config['MAILING']['toaddr'], env.config['MAILING']['password'], env.config['NETWORK']['port'])
    
    @classmethod
    def error(cls, msg):
        logging.error(msg)
        Mailer.send(msg)
        
    @classmethod
    def info(cls, msg):
        logging.info(msg)
