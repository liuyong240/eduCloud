#!/usr/bin/python -u

__version__ = '1.0.0'

import Queue
from cmdConsumerThread import *
from statusPublisherThread import *

from luhyaapi.educloudLog import *
from luhyaapi.run4everProcess import *

LOG_FILE = '/var/log/educloud/nc_daemon.log'
logger = init_log(LOG_FILE)

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

def registerMyselfasNC():
    pass


def main():
    # read /storage/config/cc.conf to register itself to cc
    registerMyselfasNC()

    # start main loop to start & monitor thread
    thread_array = ['cmdConsumerThread', 'statusPublisherThread']
    bucket = Queue.Queue()

    for daemon in thread_array:
        bucket.put(daemon)

    while True:
        try:
            daemon_name = bucket.get(block=True)
            bucket.task_done()

            logger.error("restart %s ... ..." % (daemon_name))

            obj = globals()[daemon_name](bucket, logger)
            obj.start()

        except Exception as e:
            logger.error(e.message)

if __name__ == '__main__':
    main()
