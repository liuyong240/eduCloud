from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.rabbitmqWrapper import *

import time, pika, json, os

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

    def isSameImageVersionAsServers(self):
        cc_ver  = ReadImageVersionFile(self.srcimgid)
        imginfo = getImageInfo(self.dstip, self.srcimgid)
        clc_ver = imginfo['data']['version']

        return clc_ver == cc_ver

    def needDownload(self):
        flag = True
        # if machine not exists, download
        # if machine exist,
            #  version is same as that in server, DON'T download
            #  not same as, download
        imgfilepath ="/storage/images/" + self.srcimgid + "/machine"
        if os.path.exists(imgfilepath) and self.isSameImageVersionAsServers():
            flag = False

        return flag

    def run(self):
        logger.error("enter into downloadWorkerThread run()")
        self.progress = 0

        source = "rsync://%s/luhya/%s" % (self.dstip, self.srcimgid)
        destination = "/storage/images/"

        if self.needDownload():
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
        else:
            self.progress = -100

class submitWorkerThread(threading.Thread):
    def __init__(self, dstip, tid):
        threading.Thread.__init__(self)

        self.dstip    = dstip
        self.tid      = tid
        retval = tid.split(':')
        self.srcimgid = retval[0]
        self.dstimgid = retval[1]
        self.progress = 0
        self.failed = 0

    def isFailed(self):
        return self.failed

    def getprogress(self):
        return self.progress

    def run(self):
        logger.error("enter into submitWorkerThread run()")
        self.progress = 0

        source= "/storage/images/" + self.dstimgid
        destination = "rsync://%s/luhya/" % (self.dstip)

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
        logger.error("%s: submit thread exit with code=%s", self.tid, exit_code)


class cc_rpcServerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

        self.connection = getConnection("localhost")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.channel.basic_qos(prefetch_count=1)

        self.cc_rpc_handlers = {
            'image/prepare'             : self.cc_rpc_handle_imageprepare,
            'image/submit'              : self.cc_rpc_handle_imagesubmit,
            'image/prepare/failure'     : self.cc_rpc_handle_prepare_failure,
            'image/prepare/success'     : self.cc_rpc_handle_prepare_success,
            'image/submit/failure'      : self.cc_rpc_handle_submit_failure,
            'image/submit/success'      : self.cc_rpc_handle_submit_success,
            'image/edit/running'        : self.cc_rpc_handle_image_running,
            'image/edit/stopped'        : self.cc_rpc_handle_image_stopped,
        }

        self.tasks_status = {}
        self.submit_tasks = {}

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
            if worker.isFailed():
                worker.start()
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

    def cc_rpc_handle_imagesubmit(self, ch, method, props, tid):
        if tid in self.submit_tasks and self.submit_tasks[tid] != None:
            worker = self.submit_tasks[tid]
            if worker.isFailed():
                worker.start()
            progress = worker.getprogress()
        else:
            progress = 0
            clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
            walrusinfo = getWalrusInfo(clcip)
            serverIP = walrusinfo['data']['ip0']
            worker = submitWorkerThread(serverIP, tid)
            worker.start()
            self.submit_tasks[tid] = worker

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "submitting",
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
            del self.submit_tasks[tid]

    def cc_rpc_handle_prepare_failure(self, ch, method, props, tid):
        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = prepareImageFailed(clcip, tid)

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_prepare_success(self, ch, method, props, tid):
        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = prepareImageFinished(clcip, tid)

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_submit_failure(self, ch, method, props, tid):
        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = submitImageFailed(clcip, tid)

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_submit_success(self, ch, method, props, tid):
        if tid in self.tasks_status and self.tasks_status[tid] != None:
            del self.tasks_status[tid]

        if tid in self.submit_tasks and self.submit_tasks[tid] != None:
            del self.submit_tasks[tid]

        # send http request to clc to
        #  1. add a new image record, and set it properties
        #  2. delete transaction record
        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = submitImageFinished(clcip, tid)

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

        oldversionNo = ReadImageVersionFile(self.dstimgid)
        newversionNo = IncreaseImageVersion(oldversionNo)
        WriteImageVersionFile(self.dstimgid,newversionNo)

    def cc_rpc_handle_image_running(self, ch, method, props, tid):
        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = updateVMStatus(clcip, tid, 'running')

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_image_stopped(self, ch, method, props, tid):
        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = updateVMStatus(clcip, tid, 'stopped')

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

