from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
import json, time, shutil, os, commands, zmq
import multiprocessing, memcache
from luhyaapi.zmqWrapper import *

logger = getclcdaemonlogger()

class clonehdProcess(multiprocessing.Process):
    def __init__(self, msg):
        multiprocessing.Process.__init__(self)
        self.tid = msg['tid']
        self.imgid, self.dstid, self.insid = parseTID(self.tid)
        self.uid = msg['uid']

    def run(self):
        srcfile = '/storage/images/%s/data' % self.imgid
        dstfile = '/storage/space/prv-data/%s/disk/%s/data' % (self.uid, self.imgid)

        if os.path.exists(dstfile):
            logger.error("%s %s d disk already exist, pass." % (self.uid, self.imgid))
        else:
            cmd = "su - luhya -c 'vboxmanage clonehd %s %s'" % (srcfile, dstfile)
            logger.error("clc clonehdProcess cmd = %s" % cmd)
            out = commands.getoutput(cmd)
            logger.error("clc clonehdProcess out = %s" % out)

def clc_clonehd_ddisk_handle(message):
    logger.error("--- --- ---zmq: clc_image_run_handle")
    worker = clonehdProcess(message)
    worker.start()

class clonehdPVDProcess(multiprocessing.Process):
    def __init__(self, msg):
        multiprocessing.Process.__init__(self)
        self.tid = msg['tid']
        self.imgid, self.dstid, self.insid = parseTID(self.tid)
        self.uid = msg['uid']

    def run(self):
        srcfile = '/storage/images/%s/machine' % self.imgid
        dstfile = '/storage/pimages/%s/%s/machine' % (self.uid, self.imgid)

        if os.path.exists(dstfile):
            logger.error("%s %s C disk already exist, pass." % (self.uid, self.imgid))
        else:
            cmd = "su - luhya -c 'vboxmanage clonehd %s %s' " % (srcfile, dstfile)
            logger.error("clc clonehdPVDProcess cmd = %s" % cmd)
            out = commands.getoutput(cmd)
            logger.error("clc clonehdPVDProcess out = %s" % out)

def clc_clondhd_pvd_handle(message):
    logger.error("--- --- ---zmq: clc_image_run_handle")
    worker = clonehdPVDProcess(message)
    worker.start()

clc_cmd_handlers = {
    'clonehd/ddisk'         : clc_clonehd_ddisk_handle,
    'clonehd/pvd'           : clc_clondhd_pvd_handle,
    #'image/stop'        : clc_image_stop_handle,
}

class clc_cmdConsumer():
    def __init__(self, port=CLC_CMD_QUEUE_PORT):
        logger.error("zmq: clc_cmdConsumer start running")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)

    def cmdHandle(self, body):
        logger.error('zmq: clc get msg body = %s' % body)
        try:
            message = json.loads(body)
            if message.has_key('op') and message['op'] in  clc_cmd_handlers and clc_cmd_handlers[message['op']] != None:
                logger.error("zmq: clc get cmd = %s" %  body)
                clc_cmd_handlers[message['op']](message)
            else:
                logger.error("zmq: clc get unknown cmd : %s", body)
        except Exception as e:
            logger.error("zmq: clc exception = %s", str(e))

    def run(self):
        while True:
            msg = self.socket.recv()
            self.socket.send('OK')
            self.cmdHandle(msg)


def main():
    consumer = clc_cmdConsumer()
    consumer.run()


if __name__ == '__main__':
    main()