from luhyaapi.run4everProcess import *
import time

class statusPublisherThread(run4everThread):
    def __init__(self, bucket, logger):
        run4everThread.__init__(self, bucket, logger)

    def run4ever(self):
        time.sleep(10)
        self.logger.error("status consumer is running.")
        raise Exception('statusConsumser is failed.')
