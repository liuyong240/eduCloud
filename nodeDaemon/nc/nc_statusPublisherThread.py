from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.vboxWrapper import *

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

        if isLNC():
            payload['nid']              = "lnc#" + payload['net_data']['mac0'] + "#status"
        else:
            payload['nid']              = "nc#" + payload['net_data']['mac0'] + "#status"
        return payload

    def send_node_status_to_cc(self, node_status):
        simple_send(logger, self._ccip, 'cc_status_queue', json.dumps(node_status))
