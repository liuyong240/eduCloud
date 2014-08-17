from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
import time

logger = getncdaemonlogger()

class nc_statusPublisherThread(run4everThread):
    def __init__(self, bucket, logger):
        run4everThread.__init__(self, bucket, logger)

    def run4ever(self):
        time.sleep(10)
        logger.error("status consumer is running.")
        raise Exception('statusConsumser is failed.')
