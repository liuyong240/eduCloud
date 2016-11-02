from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
import json, time, shutil, os, commands, zmq
import multiprocessing, memcache

logger = getclcdaemonlogger()

class runVMTimer(multiprocessing.Process):
    def __init__(self, msg):
        multiprocessing.Process.__init__(self)
        self.tid = msg['tid']

        #read timer seconds
        res = get_desktop_res()
        self.timer_seconds = res['boot_timer']

    def run(self):
        flag = False
        time.sleep(self.timer_seconds)
        retry_times = 5

        while (retry_times > 0):
            payload = getVMStatus("127.0.0.1", self.tid)
            if payload['state']  == "Running" or payload['state'] == "running":
                retry_times = 0
                flag = True
                logger.error("after %d seconds VM %s ALREADY running, cancel the timer." % (self.timer_seconds, self.tid))
            else:
                logger.error("after %d seconds VM %s NOT in running status, decide to stop it" % (self.timer_seconds, self.tid))

            retry_times -= 1
            time.sleep(1)

        if flag == False:
            stopVMWrapper("127.0.0.1",self.tid)


def clc_image_run_handle(message):
    logger.error("--- --- ---zmq: clc_image_run_handle")
    worker = runVMTimer(message)
    worker.start()

clc_cmd_handlers = {
    'image/run'         : clc_image_run_handle,
    #'image/stop'        : clc_image_stop_handle,
}

class clc_cmdConsumer():
    def __init__(self, port=CLC_CMD_QUEUE_PORT):
        logger.error("zmq: nc_cmd_consumer start running")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.bind("tcp://*:%s" % port)

    def cmdHandle(self, body):
        message = json.loads(body)
        if message.has_key('op') and message['op'] in  clc_cmd_handlers and clc_cmd_handlers[message['op']] != None:
            logger.error("zmq: nc get cmd = %s" %  body)
            clc_cmd_handlers[message['op']](message)
        else:
            logger.error("zmq: clc get unknown cmd : %s", body)

    def run(self):
        while True:
            msg = self.socket.recv()
            self.cmdHandle(msg)


def main():
    consumer = clc_cmdConsumer()
    consumer.run()


if __name__ == '__main__':
    main()