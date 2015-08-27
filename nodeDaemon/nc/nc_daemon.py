#!/usr/bin/python -u

__version__ = '1.0.0'

import Queue, requests
from nc_cmdConsumerThread import *
from nc_statusPublisherThread import *
from luhyaapi.educloudLog import *
from luhyaapi.luhyaTools import configuration
from luhyaapi.hostTools import *

logger = getncdaemonlogger()

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

def perform_mount():
    # mount cc's /storage/space/ to local
    if amIcc():
        logger.error("I am nc and cc, no mount any more.")
        return

    ccip = getccipbyconf()
    base_cmd = 'echo luhya | sshfs -o cache=yes,allow_other,password_stdin,reconnect luhya@%s:/storage/space /storage/space'

    if not os.path.ismount('/storage/space'):
        cmd = base_cmd % (ccip)
        os.system(cmd)

def getRuntimeOpiton():
    return ''

def registerMyselfasNC():
    ccip = getccipbyconf(mydebug=DAEMON_DEBUG)
    ccname = getccnamebyconf()

    hostname, hostcpus, hostmem, hostdisk = getHostAttr()
    netlist = getHostNetInfo()

    if isLNC():
        if DAEMON_DEBUG == True:
            url = 'http://%s:8000/cc/api/1.0/register/lnc' % ccip
        else:
            url = 'http://%s/cc/api/1.0/register/lnc' % ccip
        payload = {
            'ip': netlist['ip0'],
            'mac': netlist['mac0'],

            'name': hostname,
            'ccname': ccname,
            'location': '',

            'cores': hostcpus,
            'memory': hostmem,
            'disk': hostdisk,
            'runtime_option': getRuntimeOpiton()
        }
    else:
        if DAEMON_DEBUG == True:
            url = 'http://%s:8000/cc/api/1.0/register/server' % ccip
        else:
            url = 'http://%s/cc/api/1.0/register/server' % ccip
        payload = {
            'role': 'nc',
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
    msg = json.loads(r.content)
    if msg['Result'] == "OK":
        logger.error("register NC %s succeed !" % netlist['ip0'])
    else:
        logger.error("register NC %s failed !" % netlist['ip0'])

def main():
    # read /storage/config/cc.conf to register itself to cc
    registerMyselfasNC()

    if not isLNC():
        perform_mount()

    # start main loop to start & monitor thread
    thread_array = ['nc_cmdConsumerThread', 'nc_statusPublisherThread']
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
