from luhyaapi.run4everProcess import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.settings import *
import time, json
import requests

logger = getwalrusdaemonlogger()

class walrus_statusPublisher():
    def __init__(self):
        logger.error("walrus_status_publisher start running")

    def statusMessageHandle(self, ch, method, properties, body):
        pass

    def run(self):
        connection = getConnection("localhost")
        channel = connection.channel()
        channel.queue_declare(queue='walrus_status_queue')
        channel.basic_consume(self.statusMessageHandle,
                              queue='walrus_status_queue',
                              no_ack=True)
        channel.start_consuming()


def registerMyselfasWALRUS():
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)

    hostname, hostcpus, hostmem, hostdisk = getHostAttr()
    netlist = getHostNetInfo()
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/register/server' % clcip
    else:
        url = 'http://%s/clc/api/1.0/register/server' % clcip
    payload = {
        'role':   'walrus',
        'name':   hostname,
        'cores': hostcpus,
        'memory': hostmem,
        'disk':   hostdisk,
        'exip': netlist['exip'],
        'ip0':    netlist['ip0'],
        'ip1':    netlist['ip1'],
        'ip2':    netlist['ip2'],
        'ip3':    netlist['ip3'],
        'mac0':   netlist['mac0'],
        'mac1':   netlist['mac1'],
        'mac2':   netlist['mac2'],
        'mac3':   netlist['mac3'],
        'ccname': '',
        'hypervisor': getHypervisor(),
    }
    r = requests.post(url, data=payload)
    return r.status_code

def main():
    # read /storage/config/clc.conf to register itself to cc
    registerMyselfasWALRUS()
    publisher = walrus_statusPublisher()
    publisher.run()


if __name__ == '__main__':
    main()