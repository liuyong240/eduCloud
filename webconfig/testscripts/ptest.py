from luhyaapi.educloudLog import *
import time, random
import multiprocessing

#logger = getncdaemonlogger()
my_pboot_delay = 100
my_semaphores = multiprocessing.Semaphore(3)

def getlogdatetime():
    return time.strftime("%d/%m/%Y") + " " + time.strftime("%H:%M:%S")


class runImageTaskThread(multiprocessing.Process):
    def __init__(self, index):
        multiprocessing.Process.__init__(self)
        self.index = index

    def RandomSleep(self, start, end):
        seconds = random.randint(start, end)
        print "process %d will sleep %d seconds" % (self.index, seconds)
        time.sleep(seconds)

    def run(self):
        #with my_semaphores:
            print("process %d start " %  self.index)
            self.RandomSleep(1,10)

            print "%s process %d Start/Prepare/Run VM " % (getlogdatetime(), self.index)
            print "%s process %d RunVM for %d-%d seconds" % (getlogdatetime(), self.index, 60, 60 * 3)
            self.RandomSleep(60, 60*3)
            print "%s process %d stop" % (getlogdatetime(), self.index)

if __name__ == '__main__':
    for i in range(4):
        p = runImageTaskThread(i)
        p.start()


