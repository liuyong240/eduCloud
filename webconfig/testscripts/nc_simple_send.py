from luhyaapi.hostTools import *
from luhyaapi.luhyaTools import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.educloudLog import *

logger = getncdaemonlogger()

def collect_node_status():
        payload = { }
        payload['type']             = 'nodestatus'
        payload['service_data']     = getServiceStatus('nc')
        payload['hardware_data']    = getHostHardware()
        payload['net_data']         = getHostNetInfo()
        #payload['vm_data']          = getVMlist()

        payload['nid']              = "nc#" + payload['net_data']['mac0'] + "#status"

        return payload

def send_node_status_to_cc(node_status):
    ccip = getccipbyconf(mydebug=DAEMON_DEBUG)
    simple_send(logger, ccip, 'cc_status_queue', json.dumps(node_status))

node_status = collect_node_status()
send_node_status_to_cc(node_status)
