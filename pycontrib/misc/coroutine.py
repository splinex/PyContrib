import logging, traceback, datetime
import tornado.gen
# from sr''c.lib.mailing import Mailer

#decorator for functions that should not ever fails
def unfailable_coroutine(func):
    @tornado.gen.coroutine
    def funcWrapped(*args):
        fails = True
        result = None
        while fails:
            fails = False            
            try:
                result = yield func(*args)
            except:
                fails = True
                logging.error(traceback.format_exc())
#                 Mailer.send(traceback.format_exc())
                yield tornado.gen.Task(tornado.ioloop.IOLoop.current().add_timeout, datetime.timedelta(milliseconds=1000))
                logging.error(traceback.format_stack())
        return result
    return funcWrapped

#coroutine with logging
def reporting_coroutine(func):
    @tornado.gen.coroutine
    def funcWrapped(*args):
        result = None
        try:
            result = yield func(*args)
        except:
            logging.error(traceback.format_exc())
#             Mailer.send(traceback.format_exc())
            logging.error(traceback.format_stack())
        return result
    return funcWrapped