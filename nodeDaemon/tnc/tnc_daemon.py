#!/usr/bin/python -u

__version__ = '1.0.0'

import Queue, requests
from tnc_statusPublisherThread import *
from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *

logger = getncdaemonlogger()

def getOSDetail():
    import platform
    os_detail = platform.linux_distribution()
    return os_detail[0] + os_detail[1]

def registerMyselfasTNC():
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)

    hostname, hostcpus, hostmem, hostdisk = getHostAttr()
    netlist = getHostNetInfo()

    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/register/tnc' % clcip
    else:
        url = 'http://%s/clc/api/1.0/register/tnc' % clcip

    payload = {
        'ip':       netlist['ip0'],
        'mac':      netlist['mac0'],

        'name':     hostname,
        'osname':   getOSDetail(),
        'location': "",

        'cores':    hostcpus,
        'memory':   hostmem,
        'disk':     hostdisk,
    }
    r = requests.post(url, data=payload)
    msg = json.loads(r.content)
    if msg['Result'] == "OK":
        logger.error("register TNC %s succeed !" % netlist['ip0'])
    else:
        logger.error("register TNC %s failed !" % netlist['ip0'])


def main():
    # read /storage/config/cc.conf to register itself to cc
    registerMyselfasTNC()

    # start main loop to start & monitor thread
    thread_array = ['tnc_statusPublisherThread']
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
            time.sleep(3)

if __name__ == '__main__':
    main()
