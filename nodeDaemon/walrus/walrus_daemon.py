#!/usr/bin/python -u

__version__ = '1.0.0'

import Queue, requests
from walrus_statusPublisherThread import *
from luhyaapi.educloudLog import *
from luhyaapi.luhyaTools import configuration
from luhyaapi.hostTools import *

logger = getwalrusdaemonlogger()

'''

start a few worker thread
if there worker thread dies, restart them
list of daemon and worker thread

1. a status report daemon, periodically report walrus status to CLC's status_queue

'''
def registerMyselfasWALRUS():
    clcip = getclcipbyconf()

    hostname, hostcpus, hostmem, hostdisk = getHostAttr()
    netlist = getHostNetInfo()
    url = 'http://%s/clc/api/1.0/register/server' % clcip
    payload = {
        'role':   'walrus',
        'name':   hostname,
        'cpus':   hostcpus,
        'memory': hostmem,
        'disk':   hostdisk,
        'ip0':    netlist['ip0'],
        'ip1':    netlist['ip1'],
        'ip2':    netlist['ip2'],
        'ip3':    netlist['ip3'],
        'mac0':   netlist['mac0'],
        'mac1':   netlist['mac1'],
        'mac2':   netlist['mac2'],
        'mac3':   netlist['mac3'],
    }
    r = requests.post(url, data=payload)
    return r.status_code

def main ():
    # read /storage/config/clc.conf to register itself to cc
    registerMyselfasWALRUS()

    # start main loop to start & monitor thread
    thread_array = ['walrus_statusPublisherThread']
    bucket = Queue.Queue()

    for daemon in thread_array:
        bucket.put(daemon)

    while True:
        try:
            daemon_name = bucket.get(block=True)
            bucket.task_done()

            logger.error("restart %s ... ..." % (daemon_name))

            obj = globals()[daemon_name](bucket, logger)
            obj.daemon = True
            obj.start()

        except Exception as e:
            logger.error(e.message)

if __name__ == '__main__':
  main ()
