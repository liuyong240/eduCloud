#!/usr/bin/python -u

__version__ = '1.0.0'

import sys, os, Queue, threading
import logging
import logging.handlers
import time
import datetime

MAX_LOGFILE_BYTE = 10 * 1024 * 1024
LOG_FILE = '/var/log/educloud/nc_daemon.log'
MAX_LOG_COUNT = 10


def init_log():
    logger = logging.getLogger('')
    ch = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOGFILE_BYTE, backupCount=MAX_LOG_COUNT)
    formatter = logging.Formatter('<%(asctime)s> <%(levelname)s> <%(module)s:%(lineno)d>\t%(message)s', datefmt='%F %T')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.ERROR)
    return logger


logger = init_log()

'''
start a few worker thread
if there worker thread dies, restart them
list of daemon and worker thread

1. a cmd_queue consumer/dispatch deamon, get cmd from CC's cmd queue, and start cmd work thread

2. a status report daemon, periodically report NC/VMs status to CC's status_queue

3. legeal cmds are
3.1  image build,
       - RPC call to CC to download image from walrus
       - download image from CC cache
       - clone a new images
       - create & run vm, report access URL
3.2  image modify
       - RPC call to CC to download image from walrus
       - download image from CC cache
       - create & run vm, report access URL
3.3  image submit
       - upload ready-image to CC
       - RPC call CC to upload image to walrus
3.4  run lvd
       - RPC call to CC to download image from walrus
       - download image from CC cache
       - create & run vm
3.5  run rvd
       - RPC call to CC to download image from walrus
       - download image from CC cache
       - create & run vm
3.6  run vs
       - RPC call to CC to download image from walrus
       - download image from CC cache
       - create & run vm
'''
class run4everThread(threading.Thread):
    def __init__(self, bucket):
        threading.Thread.__init__(self)
        self.bucket = bucket

    def run4ever(self):
        pass

    def run(self):
        try:
            self.run4ever()
        except Exception:
            self.bucket.put(self.__class__.__name__)

class statusConsumerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

    def run4ever(self):
        time.sleep(10)
        logger.error("status consumer is running.")
        raise Exception('statusConsumser is failed.')


class cmdConsumerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

    def run4ever(self):
        while True:
            time.sleep(3)
            logger.error("cmd consumer is running.")
            # raise Exception('cmdConsumer is failed.')


def registerMyselfasNC():
    pass


def main():
    # read /storage/config/cc.conf to register itself to cc
    registerMyselfasNC()

    bucket = Queue.Queue()

    mydaemons = ['cmdConsumerThread', 'statusConsumerThread']
    for daemon in mydaemons:
        bucket.put(daemon)

    while True:
        try:
            daemon_name = bucket.get(block=True)
            bucket.task_done()

            logger.error("--- %s:" %  (daemon_name))

            obj = globals()[daemon_name](bucket)
            obj.start()

        except Exception as e:
            logger.error(e.message)


if __name__ == '__main__':
    main()
