'''
Tornado like ioloop over gobject ioloop 

Replacing the loop = gobject.MainLoop() with loop = ioloop.GObjectIOLoop(); loop.install()
'''

from gi.repository import GObject, GLib
import signal

import tornado.ioloop

class GObjectIOLoop(tornado.ioloop.IOLoop):
    def initialize(self):
        super(GObjectIOLoop, self).initialize()
        self._loop = GObject.MainLoop()
        self._fds = {}

    def close(self, all_fds=False):
        # TODO: remove callbacks
        if all_fds:
            for fd in self._fds:
                self.close_fd(fd)

    def time(self):
        return GObject.get_current_time()

    def add_handler(self, fd, handler, events):
        if fd in self._fds:
            raise ValueError('fd %s added twice' % fd)
            print('fd %s added twice' % fd)
        self._fds[fd] = (GObject.io_add_watch(fd, GLib.IOCondition(events), self._handle_watch),
                         handler)

    def update_handler(self, fd, events):
        tag, handler = self._fds.pop(fd)
        GObject.source_remove(tag)
        self.add_handler(fd, handler, events)

    def remove_handler(self, fd):
        tag, _ = self._fds.pop(fd)
        GObject.source_remove(tag)

    def _handle_watch(self, fd, events):
        self._fds[fd][1](fd, events)
        return True

    def set_blocking_signal_threshold(self, seconds, action):
        if seconds is not None:
            signal.signal(signal.SIGALRM,
                          action if action is not None else signal.SIG_DFL)

    def start(self):
        self._loop.run()
        pass

    def stop(self):
        self._loop.quit()

    def _handle_call_at(self, callback):
        def handle_callback(*args, **kwargs):
            callback(*args, **kwargs)
            return False
        return handle_callback

    def call_at(self, when, callback, *args, **kwargs):
        interval = (when - self.time()) * 1000
        return GObject.timeout_add(int(interval), self._handle_call_at(callback), *args, **kwargs)

    def remove_timeout(self, timeout):
        GObject.source_remove(timeout)

    def add_callback(self, callback, *args, **kwargs):
        return GObject.idle_add(
            self._handle_callback, callback, *args, **kwargs)

    def add_callback_from_signal(self, callback, *args, **kwargs):
        self.add_callback(callback, *args, **kwargs)

    def _handle_callback(self, callback, *args, **kwargs):
        self._run_callback(lambda: callback(*args, **kwargs))
        return False
