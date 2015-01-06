from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.rabbitmqWrapper import *

import time, pika, json, os

logger = getccdaemonlogger()

class cc_rpcServerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

        self.connection = getConnection("localhost")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.channel.basic_qos(prefetch_count=1)

        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        walrusinfo = getWalrusInfo(clcip)
        self.serverIP = walrusinfo['data']['ip0']

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
            self.cc_rpc_handlers[message['op']](ch, method, props, message['tid'], message['paras'])
        else:
            logger.error("unknow cmd : %s", message['op'])

    def cc_rpc_handle_imageprepare(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_imageprepare")

        prompt = 'Downloading file from Walrus to CC ... ...'
        if paras == 'luhya':
            prompt = 'Downloading image file from Walrus to CC ... ...'
            source      = "rsync://%s/%s/%s" % (self.serverIP, 'luhya', tid.split(':')[0])
            destination = "/storage/images/"
        if paras == 'db':
            prompt = 'Downloading database file from Walrus to CC ... ...'
            source      = "rsync://%s/%s/%s" % (self.serverIP, 'db', tid.split(':')[0])
            destination = "/storage/space/database/"

        if tid in self.tasks_status and self.tasks_status[tid] != None:
            worker = self.tasks_status[tid]
        else:
            worker = rsyncWorkerThread(logger, source, destination)
            worker.start()
            self.tasks_status[tid] = worker

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "prepare",
                'state'     : 'downloading',
                'progress'  : worker.getprogress(),
                'tid'       : tid,
                'prompt'    : prompt,
                'errormsg'  : worker.getErrorMsg(),
                'failed'    : worker.isFailed(),
                'done'      : worker.isDone(),
        }
        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

        if worker.isFailed() or worker.isDone():
            del self.tasks_status[tid]

    def cc_rpc_handle_imagesubmit(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_imagesubmit")

        prompt = 'Uploading file from CC to Walrus ... ...'
        if paras == 'luhya':
            prompt      = 'Uploading image file from CC to Walrus ... ...'
            source      = "/storage/images/%s" % tid.split(':')[1]
            destination = "rsync://%s/%s/" % (self.serverIP, 'luhya')
        if paras == 'db':
            prompt      = 'Uploading database file from CC to Walrus ... ...'
            source      = '/storage/space/database/%s' %  tid.split(':')[1]
            destination = "rsync://%s/%s/" % (self.serverIP, 'db')

        if tid in self.submit_tasks and self.submit_tasks[tid] != None:
            worker = self.submit_tasks[tid]
        else:
            worker = rsyncWorkerThread(logger, source, destination)
            worker.start()
            self.submit_tasks[tid] = worker

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "submitting",
                'state'     : 'uploading',
                'progress'  : worker.getprogress(),
                'tid'       : tid,
                'prompt'    : prompt,
                'errormsg'  : worker.getErrorMsg(),
                'failed'    : worker.isFailed(),
                'done'      : worker.isDone(),
        }
        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

        if worker.isFailed() or worker.isDone():
            del self.submit_tasks[tid]

    def cc_rpc_handle_prepare_failure(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_prepare_failure")

        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = prepareImageFailed(clcip, tid)

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_prepare_success(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_prepare_success")

        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = prepareImageFinished(clcip, tid)

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_submit_failure(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_submit_failure")

        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = submitImageFailed(clcip, tid)

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_submit_success(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_submit_success")

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

    def cc_rpc_handle_image_running(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_image_running")

        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = updateVMStatus(clcip, tid, 'running')

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def cc_rpc_handle_image_stopped(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_image_stopped")

        clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        payload = updateVMStatus(clcip, tid, 'stopped')

        payload = json.dumps(payload)
        ch.basic_publish(
                 exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=payload)
        ch.basic_ack(delivery_tag = method.delivery_tag)

