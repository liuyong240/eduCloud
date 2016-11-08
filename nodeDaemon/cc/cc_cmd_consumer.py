# coding=UTF-8
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.settings import *
from luhyaapi.zmqWrapper import *
import multiprocessing
import time, json, os

logger = getccdaemonlogger()
img_tasks_status = {}
db_tasks_status = {}
submit_tasks = {}


def cc_rpc_handle_imageprepare(msg):
    tid   = msg['tid']
    paras = msg['paras']
    logger.error("--- --- --- cc_rpc_handle_imageprepare : %s" % tid)
    locale_string = getlocalestring()
    serverIP = getclcipbyconf(mydebug=DAEMON_DEBUG)
    try:
        prompt = 'Downloading file from Walrus to CC ... ...'
        if paras == 'luhya':
            prompt = locale_string['promptDfromWarlus2CC_image']
            source = "rsync://%s/%s/%s" % (serverIP, 'luhya', tid.split(':')[0])
            destination = "/storage/images/"

            imgid = tid.split(':')[0]
            if imgid in img_tasks_status.keys():
                if not tid in img_tasks_status[imgid]['tids']:
                    img_tasks_status[imgid]['tids'].apppend(tid)
                worker = img_tasks_status[imgid]['worker']
            else:
                img_tasks_status[imgid] = {}
                img_tasks_status[imgid]['tids'] = [tid]
                worker = rsyncWorkerThread(logger, source, destination)
                worker.start()
                img_tasks_status[imgid]['worker'] = worker

        if paras == 'db':
            prompt = locale_string['promptDfromWarlus2CC_db']
            insid = tid.split(':')[2]
            if insid.find('TMP') == 0:
                source = "rsync://%s/%s/%s" % (serverIP, 'db', tid.split(':')[0])
                destination = "/storage/space/database/images/"
                imgid = tid.split(':')[0]
            else:
                source = "rsync://%s/%s/%s" % (serverIP, 'vss', tid.split(':')[2])
                destination = "/storage/space/database/instances/"
                imgid = tid.split(':')[2]

            if imgid in db_tasks_status.keys():
                if not tid in db_tasks_status[imgid]['tids']:
                    db_tasks_status[imgid]['tids'].apppend(tid)
                worker = db_tasks_status[imgid]['worker']
            else:
                db_tasks_status[imgid] = {}
                db_tasks_status[imgid]['tids'] = [tid]
                worker = rsyncWorkerThread(logger, source, destination)
                worker.start()
                db_tasks_status[imgid]['worker'] = worker

        payload = {
            'type': 'taskstatus',
            'phase': "preparing",
            'state': 'downloading',
            'progress': worker.getprogress(),
            'tid': tid,
            'prompt': prompt,
            'errormsg': worker.getErrorMsg(),
            'failed': worker.isFailed(),
            'done': worker.isDone(),
        }
        #zmq_send(ccip, json.dumps(payload), NC_CMD_QUEUE_PORT)

        if worker.isFailed() or worker.isDone():
            if paras == 'luhya':
                del img_tasks_status[imgid]
            if paras == 'db':
                del db_tasks_status[imgid]

    except Exception as e:
        logger.error("cc_rpc_handle_imageprepare Exception Error Message : %s" % str(e))


def cc_rpc_handle_imagesubmit(msg):
    pass

def cc_rpc_handle_prepare_failure(msg):
    pass

def cc_rpc_handle_prepare_success(msg):
    pass

def cc_rpc_handle_submit_failure(msg):
    pass

def cc_rpc_handle_submit_success(msg):
    pass

def cc_rpc_handle_image_running(msg):
    pass

def cc_rpc_handle_image_stopped(msg):
    pass

cc_rpc_handlers = {
    'image/prepare':            cc_rpc_handle_imageprepare,
    'image/submit':             cc_rpc_handle_imagesubmit,
    'image/prepare/failure':    cc_rpc_handle_prepare_failure,
    'image/prepare/success':    cc_rpc_handle_prepare_success,
    'image/submit/failure':     cc_rpc_handle_submit_failure,
    'image/submit/success':     cc_rpc_handle_submit_success,
    'image/edit/running':       cc_rpc_handle_image_running,
    'image/edit/stopped':       cc_rpc_handle_image_stopped,
}

class cc_cmdConsumer():
    def __init__(self, port=CC_CMD_QUEUE_PORT):
        logger.error("zmq: cc_cmd_consumer start running")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)
        self.ret = {}

    def cmdHandle(self, body):
        logger.error("zmq: get cmd body = %s" % body)
        try:
            message = json.loads(body)
            if message.has_key('op') and message['op'] in  cc_rpc_handlers and cc_rpc_handlers[message['op']] != None:
                p = multiprocessing.Process(target=cc_rpc_handlers[message['op']], args=(message,))
                p.start()
                #cc_rpc_handlers[message['op']](message)
            else:
                logger.error("zmq: nc get unknown cmd : %s", body)
        except Exception as e:
            logger.error("zmq: exception =  %s" % str(e))

    def run(self):
        while True:
            msg = self.socket.recv()
            self.cmdHandle(msg)
            self.socket.send('OK')



def main():
    consumer = cc_cmdConsumer()
    consumer.run()


if __name__ == '__main__':
    main()