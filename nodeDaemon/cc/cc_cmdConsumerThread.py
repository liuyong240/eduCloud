from luhyaapi.run4everProcess import *
import time

class cc_cmdConsumerThread(run4everThread):
    def __init__(self, bucket, logger):
        run4everThread.__init__(self, bucket, logger)

    def run4ever(self):
        while True:
            time.sleep(3)
            self.logger.error("cmd consumer is running.")
            # raise Exception('cmdConsumer is failed.')
