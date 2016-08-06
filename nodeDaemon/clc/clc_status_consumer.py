from luhyaapi.run4everProcess import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
import time, json
import memcache
import requests

logger = getclcdaemonlogger()

class clc_statusConsumer():
    def __init__(self):
        logger.error("clc_status_consumer start running")
        self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    def save2Mem(self, key, msg):
        try:
            self.mc.set(key, msg, 5*60)
        except Exception as e:
            logger.errro(str(e))

    def forwardMessage2Memcache(self, message):
        flag = 0
        json_msg = json.loads(message)
        if json_msg['type'] == 'taskstatus':
            key = str(json_msg['tid'])
            flag = 1
        elif json_msg['type'] == 'nodestatus':
            key = str(json_msg['nid'])
        elif json_msg['type'] == 'ccstatus':
            key = str(json_msg['ccid'])

        self.save2Mem(key, message)

        # test save is ok
        if flag == 1:
            payload = self.mc.get(key)
            logger.error("thomas#load %s=%s" % (key, payload))

    def statusMessageHandle(self, ch, method, properties, body):
        self.forwardMessage2Memcache(body)

    def run(self):
        connection = getConnection("localhost")
        channel = connection.channel()
        channel.queue_declare(queue='clc_status_queue')
        channel.basic_consume(self.statusMessageHandle,
                              queue='clc_status_queue',
                              no_ack=True)
        channel.start_consuming()


def registerMyselfasCLC():
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)

    hostname, hostcpus, hostmem, hostdisk = getHostAttr()
    netlist = getHostNetInfo()
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/register/server' % clcip
    else:
        url = 'http://%s/clc/api/1.0/register/server' % clcip
    payload = {
        'role': 'clc',
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
        'hypervisor': getHypervisor(),
        'ccname':'',
    }
    r = requests.post(url, data=payload)
    return r.status_code

def main():
    # read /storage/config/clc.conf to register itself to cc
    registerMyselfasCLC()
    consumer = clc_statusConsumer()
    consumer.run()


if __name__ == '__main__':
    main()