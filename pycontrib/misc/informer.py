from copy import deepcopy
import logging
import logging.handlers
import smtplib


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
            # logging.error('Mailer was not inited')
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

class MultilineFormatter(logging.Formatter):
    def format(self, record):
        ret = str()
        msg_raws = deepcopy(record.getMessage())
        record.args = ()
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            record.exc_info = None
        else:
            exc_text = None

        for msg_raw in msg_raws.split('\n'):
            record.msg = msg_raw
            if ret:
                ret += '\n'
            ret += super().format(record)

        if exc_text:
            for exc_raw in exc_text.split('\n'):
                record.msg = exc_raw
                if ret:
                    ret += '\n'
                ret += super().format(record)

        return ret

class Informer(object):

    @classmethod
    def initEnv(cls, env, redefine_tornado_logging=False):
        logging_level = logging.INFO if env.debug else logging.ERROR
        Informer.log = logging.getLogger(env.name)
        Informer.log.propagate = False
        Informer.log.setLevel(logging_level)

        if env.log == 'syslog':
            handler = logging.handlers.SysLogHandler('/dev/log')
        elif env.log == '/dev/stdout':
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(env.log)

        formatter = MultilineFormatter('{0}[{1}] %(levelname)s: %(message)s'.format(env.name, env.port))
        handler.setFormatter(formatter)
        Informer.log.addHandler(handler)

        if redefine_tornado_logging:
            for logger_name in ('tornado.access', 'tornado.application', 'tornado.general'):
                logger = logging.getLogger(logger_name)
                logger.handlers = []
                logger.addHandler(handler)
                logger.setLevel(logging_level)

        if 'MAILING' in env.config and env.config['MAILING']['enabled'] == 'True':
            Mailer.initCredentials(env.name, env.config['MAILING']['smtpserver'], env.config['MAILING']['fromaddr'],
                                          env.config['MAILING']['toaddr'], env.config['MAILING']['password'], env.config['NETWORK']['port'])

    @classmethod
    def error(cls, msg):
        Informer.log.error(msg)
        Mailer.send(msg)

    @classmethod
    def warning(cls, msg):
        Informer.log.warning(msg)

    @classmethod
    def info(cls, msg):
        Informer.log.info(msg)

    @classmethod
    def mail(cls, msg):
        Mailer.send(msg)
