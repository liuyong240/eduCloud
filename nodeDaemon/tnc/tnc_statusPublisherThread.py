from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *
from luhyaapi.rabbitmqWrapper import *

import time

logger = getncdaemonlogger()

class tnc_statusPublisherThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)
        self._clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        logger.error("clc ip = %s" % self._clcip)

    def run4ever(self):
        while True:
            try:
                node_status = self.collect_node_status()
                self.send_node_status_to_cc(node_status)
                time.sleep(10*60)
            except Exception as e:
                logger.error('tnc_statusPublisherThread exception = %s' % str(e))

    def collect_node_status(self):
        payload = { }
        payload['type']             = 'terminal_status'
        try:
            payload['net_data']         = getHostNetInfo()
        except Exception as e:
            logger.error('getHostNetInfo exception = %s' % str(e))


        payload['nid']              = "tnc#" + payload['net_data']['mac0'] + "#status"
        return payload

    def send_node_status_to_cc(self, node_status):
        simple_send(logger, self._clcip, 'clc_status_queue', json.dumps(node_status))
