#!/usr/bin/python -u

__version__ = '1.0.0'

import Queue,requests

from cc_cmdConsumerThread import *
from cc_statusPublisherThread import *
from cc_statusConsumerThread import *
from cc_rpcServerThread import *

from luhyaapi.educloudLog import *
from luhyaapi.luhyaTools import configuration
from luhyaapi.hostTools import *

logger = getccdaemonlogger()

'''

start a few worker thread
if there worker thread dies, restart them
list of daemon and worker thread

1. a status_queue consumer deamon, after process based on message type, forwarding to CLC's status_queue

2. a status report daemon, periodically report CC status to CLC's status_queue

3. a cmd_queue comsumer daemon for handler RPC like
3.1  download image from walrus
3.2  upload image to walrus

'''
def perform_mount():
    # mount clc's /storage/space/{software, pub-data} to local
    if amIwalrus():
        logger.error("I am cc and walrus, no mount any more.")
        return

    clcip = getclcipbyconf()
    base_cmd = 'echo luhya | sshfs -o cache=yes,allow_other,password_stdin,reconnect luhya@%s:/storage/space /storage/space'

    if not os.path.ismount('/storage/space'):
        cmd1 = base_cmd % (clcip)
        logger.error(cmd1)
        os.system(cmd1)

def registerMyselfasCC():
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
    ccname = getccnamebyconf()

    hostname, hostcpus, hostmem, hostdisk = getHostAttr()
    netlist = getHostNetInfo()
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/register/server' % clcip
    else:
        url = 'http://%s/clc/api/1.0/register/server' % clcip
    payload = {
        'role': 'cc',
        'name': hostname,
        'cores': hostcpus,
        'memory': hostmem,
        'disk': hostdisk,
        'exip': netlist['exip'],
        'ip0': netlist['ip0'],
        'ip1': netlist['ip1'],
        'ip2': netlist['ip2'],
        'ip3': netlist['ip3'],
        'mac0': netlist['mac0'],
        'mac1': netlist['mac1'],
        'mac2': netlist['mac2'],
        'mac3': netlist['mac3'],
        'ccname': ccname,
    }
    r = requests.post(url, data=payload)
    return r.status_code


def main():
    # read /storage/config/cc.conf to register itself to cc
    registerMyselfasCC()

    perform_mount()

    # start main loop to start & monitor thread
    # thread_array = ['cc_statusPublisherThread', 'cc_statusConsumerThread', 'cc_rpcServerThread']
    thread_array = ['cc_rpcServerThread', 'cc_statusConsumerThread', 'cc_statusPublisherThread']
    bucket = Queue.Queue()

    for daemon in thread_array:
        bucket.put(daemon)

    while True:
        try:
            daemon_name = bucket.get(block=True)
            bucket.task_done()

            logger.error("restart %s ... ..." % (daemon_name))

            obj = globals()[daemon_name](bucket)
            obj.daemon = True
            obj.start()

        except Exception as e:
            logger.error(str(e))


if __name__ == '__main__':
    main()
