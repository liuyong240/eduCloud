from luhyaapi.educloudLog import *
import time
import multiprocessing

logger = getncdaemonlogger()
my_pboot_delay = 10
my_semaphores = multiprocessing.Semaphore(3)
class runImageTaskThread(multiprocessing.Process):
    def __init__(self, index):
        multiprocessing.Process.__init__(self)
        self.index = index

    def run(self):
        with my_semaphores:
            logger.error("process %s start" %  self.index)
            time.sleep(my_pboot_delay)
            logger.error("process %s stop" % self.index)

for i in range(10):
    p = runImageTaskThread(i)
    p.start()


