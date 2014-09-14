from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.rabbitmqWrapper import *

import time, pika, json

logger = getccdaemonlogger()

class downloadWorkerThread(threading.Thread):
    def __init__(self, dstip, tid):
        threading.Thread.__init__(self)

        self.dstip    = dstip
        self.tid      = tid
        retval = tid.split(':')
        self.srcimgid = retval[0]
        self.progress = 0
        self.failed = 0

    def isFailed(self):
        return self.failed

    def getprogress(self):
        return self.progress

    def run(self):
        logger.error("enter into downloadWorkerThread run()")
        self.progress = 0

        source = "rsync://%s/luhya/%s" % (self.dstip, self.srcimgid)
        destination = "/storage/images/"
        rsync = rsyncWrapper(source, destination)
        rsync.startRsync()

        while rsync.isRsyncLive():
            tmpfilesize, pct, bitrate, remain = rsync.getProgress()
            msg = "%s  %s %s %s" % (tmpfilesize, pct, bitrate, remain)
            logger.error("luhya:%s", msg)
            self.progress = int(pct.split('%')[0])

        exit_code = rsync.getExitStatus()
        if exit_code == 0:
            self.progress = -100
        else:
            self.progress = exit_code
            self.failed   = 1
        logger.error("%s: download thread exit with code=%s", self.tid, exit_code)

class cc_rpcServerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

        self.connection = getConnection("localhost")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.channel.basic_qos(prefetch_count=1)

        self.cc_rpc_handlers = {
            'image/prepare'    : self.cc_rpc_handle_imageprepare,
        }

        self.tasks_status = {}

    def run4ever(self):
        self.channel.basic_consume(self.on_request, queue='rpc_queue')
        self.channel.start_consuming()

    def on_request(self, ch, method, props, body):
        logger.error("get rpc cmd = %s" % body)
        message = json.loads(body)

        if message['op'] in self.cc_rpc_handlers and self.cc_rpc_handlers[message['op']] != None:
            self.cc_rpc_handlers[message['op']](ch, method, props, message['paras'])
        else:
            logger.error("unknow cmd : %s", message['op'])


    def cc_rpc_handle_imageprepare(self, ch, method, props, tid):
        if tid in self.tasks_status and self.tasks_status[tid] != None:
            worker = self.tasks_status[tid]
            progress = worker.getprogress()
        else:
            progress = 0
            clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
            walrusinfo = getWalrusInfo(clcip)
            serverIP = walrusinfo['data']['ip0']
            worker = downloadWorkerThread(serverIP, tid)
            worker.start()
            self.tasks_status[tid] = worker

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "downloading",
                'progress'  : progress,
                'tid'       : tid,
                'errormsg'  : '',
                'failed'    : worker.isFailed()
        }
        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

        if progress < 0:
            del self.tasks_status[tid]


