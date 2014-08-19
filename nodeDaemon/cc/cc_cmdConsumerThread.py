from luhyaapi.run4everProcess import *
import time

class cc_cmdConsumerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

    def run4ever(self):
        while True:
            time.sleep(3)
