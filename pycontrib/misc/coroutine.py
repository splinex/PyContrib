import traceback, datetime
import tornado.gen
from pycontrib.misc.informer import Informer
# from sr''c.lib.mailing import Mailer

# decorator for functions that should not ever fails
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
                Informer.error(traceback.format_exc())
#                 Mailer.send(traceback.format_exc())
                yield tornado.gen.Task(tornado.ioloop.IOLoop.current().add_timeout, datetime.timedelta(milliseconds=1000))
                Informer.error(traceback.format_stack())
        raise tornado.gen.Return(result)
#         return result
    return funcWrapped

# coroutine with logging
def reporting_coroutine(func):
    @tornado.gen.coroutine
    def funcWrapped(*args):
        result = None
        try:
            result = yield func(*args)
        except:
            pass
#             Informer.error(traceback.format_exc())
#             Mailer.send(traceback.format_exc())
#             Informer.error(traceback.format_stack())
        raise tornado.gen.Return(result)
#         return result
    return funcWrapped
