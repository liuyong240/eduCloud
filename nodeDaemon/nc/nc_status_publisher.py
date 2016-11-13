from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.vboxWrapper import *

import time, psutil, requests

logger = getncdaemonlogger()

class nc_statusPublisher():
    def __init__(self, ):
        logger.error("nc_status_publisher start running")
        self._ccip = getccipbyconf(mydebug=DAEMON_DEBUG)
        logger.error("cc ip = %s" % self._ccip)

    def run(self):
        while True:
            try:
                node_status = self.collect_node_status()
                self.send_node_status_to_cc(node_status)
                time.sleep(5*60)
            except Exception as e:
                logger.error('nc_statusPublisherThread exception = %s' % str(e))

    def collect_node_status(self):
        payload = { }
        payload['type']             = 'nodestatus'
        try:
            payload['service_data']     = getServiceStatus('nc')
        except Exception as e:
            logger.error('getServiceStatus exception = %s' % str(e))
        try:
            payload['hardware_data']    = getHostHardware()
            logger.error("nc_statusPublisher-hardware data %s" % json.dumps(payload['hardware_data']))
        except Exception as e:
            logger.error('getHostHardware exception = %s' % str(e))
        try:
            payload['net_data']         = getHostNetInfo()
        except Exception as e:
            logger.error('getHostNetInfo exception = %s' % str(e))
        try:
            payload['vm_data']          = getVMlist()
        except Exception as e:
            logger.error('getVMlist exception = %s' % str(e))

        payload['nid']              = "nc#" + payload['net_data']['mac0'] + "#status"
        return payload

    def send_node_status_to_cc(self, node_status):
        simple_send(logger, self._ccip, 'cc_status_queue', json.dumps(node_status))


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
            'hypervisor': getHypervisor(),

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
            'hypervisor': getHypervisor(),
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

    publisher = nc_statusPublisher()
    publisher.run()


if __name__ == '__main__':
    main()

