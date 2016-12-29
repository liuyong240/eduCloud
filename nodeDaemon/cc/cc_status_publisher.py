from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.settings import *

import time, psutil

logger = getccdaemonlogger()

class cc_statusPublisherThread():
    def __init__(self, ):
        logger.error("cc_status_publisher start running")
        self._clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        logger.error("clc ip = %s" % self._clcip)

    def run(self):
        while True:
            cc_status = self.collect_cc_status()
            self.send_node_status_to_clc(cc_status)
            time.sleep(5*60)

    def collect_cc_status(self):
        payload = { }
        payload['type']             = 'ccstatus'
        payload['service_data']     = getServiceStatus('cc')
        payload['hardware_data']    = getHostHardware()
        payload['net_data']         = getHostNetInfo()

        payload['ccid']              = "cc#" + payload['net_data']['mac0'] + "#status"

        return payload

    def send_node_status_to_clc(self, node_status):
        simple_send(logger, self._clcip, 'clc_status_queue', json.dumps(node_status))

def main():
    publisher = cc_statusPublisherThread()
    publisher.run()

if __name__ == '__main__':
    main()