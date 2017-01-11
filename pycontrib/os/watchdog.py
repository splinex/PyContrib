#! /usr/bin/python3

'''
Watchdog service
'''

import asyncio
import logging
from os.path import getmtime
import sys

logger = logging.getLogger('watchdog')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[Watchdog] %(levelname)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class SubprocessWatchdog:

    def __init__(self, executor_script, state_file):
        self.executor_script = executor_script
        self.state_file = state_file
        self.process = None
        self.state_file_mtime = None

    @asyncio.coroutine
    def run(self):
        try:
            self.process = yield from asyncio.create_subprocess_exec(self.executor_script)
        except:
            logger.error('Can not run {}'.format(self.executor_script))

    @asyncio.coroutine
    def stop(self):
        if self.process_is_alive():
            try:
                self.process.terminate()
                yield from self.process.wait()
            except ProcessLookupError:
                self.process = None
            else:
                logger.info('Stopped')

    def get_state_file_mtime(self):
        try:
            mtime = getmtime(self.state_file)
        except FileNotFoundError:
            mtime = 0
        return mtime

    def process_is_alive(self):
        return self.process is not None and self.process.pid is not None

    async def watch(self):
        logger.info('Going to start {}'.format(self.executor_script))
        await self.run()
        await asyncio.sleep(40)
        while True:
            await asyncio.sleep(20)
            if self.process_is_alive():
                mtime = self.get_state_file_mtime()
                if mtime == self.state_file_mtime:
                    logger.info('Status file {} was not changed'.format(self.state_file))
                else:
                    self.state_file_mtime = mtime
                    continue
            else:
                logger.info('No alive process')

            logger.info('Going to restart {}'.format(self.executor_script))
            await self.stop()
            await asyncio.sleep(10)
            await self.run()
            await asyncio.sleep(40)

def main():

    loop = asyncio.get_event_loop()

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    if len(sys.argv) < 3:
        logger.info('Usage: me.py script_to_execute state_file')
        return

    executor_script, state_file = sys.argv[1:3]

    subprocess_watchdog = SubprocessWatchdog(executor_script, state_file)

    loop.run_until_complete(subprocess_watchdog.watch())
    loop.close()

if __name__ == '__main__':
    main()
