from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *
from luhyaapi.rabbitmqWrapper import *

import time, psutil

logger = getncdaemonlogger()

class nc_statusPublisherThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)
        self._ccip = getccipbyconf(mydebug=DAEMON_DEBUG)
        logger.error("cc ip = %s" % self._ccip)

    def run4ever(self):
        while True:
            try:
                node_status = self.collect_node_status()
                self.send_node_status_to_cc(node_status)
                time.sleep(5*60)
            except Exception as e:
                logger.error('nc_statusPublisherThread exception = %s' % e.message)

    def collect_node_status(self):

        payload = { }
        payload['type']             = 'nodestatus'
        payload['service_data']     = getServiceStatus('nc')
        payload['hardware_data']    = getHostHardware()
        payload['net_data']         = getHostNetInfo()
        payload['vm_data']          = getVMlist()

        payload['nid']              = "nc#" + payload['net_data']['mac0'] + "#status"

        return payload

    def send_node_status_to_cc(self, node_status):
        simple_send(logger, self._ccip, 'cc_status_queue', json.dumps(node_status))
