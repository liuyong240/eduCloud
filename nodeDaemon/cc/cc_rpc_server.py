# coding=UTF-8
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.settings import *

import time, pika, json, os

logger = getccdaemonlogger()

class cc_rpcServer():
    def __init__(self,):
        logger.error("cc_rpc_server start running")
        self.connection = getConnection("localhost")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.channel.basic_qos(prefetch_count=1)

        self.clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
        # walrusinfo = getWalrusInfo(self.clcip)
        # self.serverIP = walrusinfo['data']['ip0']
        self.serverIP = self.clcip

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

        self.img_tasks_status = {}
        self.db_tasks_status = {}
        self.submit_tasks = {}

    def run(self):
        self.channel.basic_consume(self.on_request, queue='rpc_queue')
        self.channel.start_consuming()

    def on_request(self, ch, method, props, body):
        logger.error("get rpc cmd = %s" % body)
        try:
            message = json.loads(body)

            if message['op'] in self.cc_rpc_handlers and self.cc_rpc_handlers[message['op']] != None:
                self.cc_rpc_handlers[message['op']](ch, method, props, message['tid'], message['paras'])
            else:
                logger.error("unknow cmd : %s", message['op'])
        except Exception as e:
            logger("error msg = %s with body=%s" % (str(e), body))

    def cc_rpc_handle_imageprepare(self, ch, method, props, tid, paras):
        logger.error("--- --- --- cc_rpc_handle_imageprepare : %s" % tid)
        locale_string = getlocalestring()
        try:
            prompt = 'Downloading file from Walrus to CC ... ...'
            if paras == 'luhya':
                prompt = locale_string['promptDfromWarlus2CC_image']
                source      = "rsync://%s/%s/%s" % (self.serverIP, 'luhya', tid.split(':')[0])
                destination = "/storage/images/"

                imgid = tid.split(':')[0]
                if imgid in self.img_tasks_status.keys():
                    if not tid in self.img_tasks_status[imgid]['tids']:
                        self.img_tasks_status[imgid]['tids'].apppend(tid)
                    worker = self.img_tasks_status[imgid]['worker']
                else:
                    self.img_tasks_status[imgid]= {}
                    self.img_tasks_status[imgid]['tids'] = [tid]
                    worker = rsyncWorkerThread(logger, source, destination)
                    worker.start()
                    self.img_tasks_status[imgid]['worker'] = worker

            if paras == 'db':
                prompt = locale_string['promptDfromWarlus2CC_db']
                insid = tid.split(':')[2]
                if insid.find('TMP') == 0:
                    source      = "rsync://%s/%s/%s" % (self.serverIP, 'db', tid.split(':')[0])
                    destination = "/storage/space/database/images/"
                    imgid = tid.split(':')[0]
                else:
                    source      = "rsync://%s/%s/%s" % (self.serverIP, 'vss', tid.split(':')[2])
                    destination = "/storage/space/database/instances/"
                    imgid = tid.split(':')[2]

                if imgid in self.db_tasks_status.keys():
                    if not tid in self.db_tasks_status[imgid]['tids']:
                        self.db_tasks_status[imgid]['tids'].apppend(tid)
                    worker = self.db_tasks_status[imgid]['worker']
                else:
                    self.db_tasks_status[imgid]= {}
                    self.db_tasks_status[imgid]['tids'] = [tid]
                    worker = rsyncWorkerThread(logger, source, destination)
                    worker.start()
                    self.db_tasks_status[imgid]['worker'] = worker

            payload = {
                    'type'      : 'taskstatus',
                    'phase'     : "preparing",
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
                if paras == 'luhya':
                    del self.img_tasks_status[imgid]
                if paras == 'db':
                    del self.db_tasks_status[imgid]

        except Exception as e:
            logger.error("cc_rpc_handle_imageprepare Exception Error Message : %s" % str(e))

    def cc_rpc_handle_imagesubmit(self, ch, method, props, tid, paras):
        locale_string = getlocalestring()
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "submitting",
            'state'     : 'uploading',
            'progress'  : 0,
            'tid'       : tid,
            'prompt'    : '',
            'errormsg'  : '',
            'failed'    : 0,
            'done'      : 0,
        }

        prompt = locale_string['promptUfromCC2Walrus_image']

        if amIclc():
            payload['prompt']   = prompt
            payload['prompt']   = prompt
            payload['done']     = 1
            payload = json.dumps(payload)
            ch.basic_publish(
                     exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=payload)
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return

        try:
            logger.error("--- --- --- cc_rpc_handle_imagesubmit")
            insid = tid.split(':')[2]
            dstid = tid.split(':')[1]

            if paras == 'luhya':
                prompt      = locale_string['promptUfromCC2Walrus_image']
                source      = "/storage/images/%s" % tid.split(':')[1]
                destination = "rsync://%s/%s/" % (self.serverIP, 'luhya')
            if paras == 'db':
                prompt      = locale_string['promptUfromCC2Walrus_db']
                destination = "rsync://%s/%s/" % (self.serverIP, 'db')
                if insid.find('TMP') == 0:
                    source      = '/storage/space/database/images/%s' %  dstid
                if insid.find('VS')  == 0:
                    payload['progress'] = 100
                    payload['prompt']   = prompt
                    payload['done']     = 1

                    payload = json.dumps(payload)
                    ch.basic_publish(
                             exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id = props.correlation_id),
                             body=payload)
                    ch.basic_ack(delivery_tag = method.delivery_tag)
                    return

            if tid in self.submit_tasks and self.submit_tasks[tid] != None:
                worker = self.submit_tasks[tid]
            else:
                worker = rsyncWorkerThread(logger, source, destination)
                worker.start()
                self.submit_tasks[tid] = worker

            payload['progress'] = worker.getprogress()
            payload['prompt']   = prompt
            payload['errormsg'] = worker.getErrorMsg()
            payload['failed']   = worker.isFailed()
            payload['done']     = worker.isDone()
            payload = json.dumps(payload)
            ch.basic_publish(
                     exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=payload)
            ch.basic_ack(delivery_tag = method.delivery_tag)

            if worker.isFailed() or worker.isDone():
                del self.submit_tasks[tid]
        except Exception as e:
            logger.error("cc_rpc_handle_imagesubmit Exception Error Message : %s" % str(e))

    def cc_rpc_handle_prepare_failure(self, ch, method, props, tid, paras):
        try:
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
        except Exception as e:
            logger.error("cc_rpc_handle_prepare_failure Exception Error Message : %s" % str(e))

    def cc_rpc_handle_prepare_success(self, ch, method, props, tid, paras):
        try:
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
        except Exception as e:
            logger.error("cc_rpc_handle_prepare_success Exception Error Message : %s" % str(e))

    def cc_rpc_handle_submit_failure(self, ch, method, props, tid, paras):
        try:
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
        except Exception as e:
            logger.error("cc_rpc_handle_submit_failure Exception Error Message : %s" % str(e))

    def cc_rpc_handle_submit_success(self, ch, method, props, tid, paras):
        try:
            logger.error("--- --- --- cc_rpc_handle_submit_success")

            if tid in self.img_tasks_status and self.img_tasks_status[tid] != None:
                del self.img_tasks_status[tid]

            if tid in self.submit_tasks and self.submit_tasks[tid] != None:
                del self.submit_tasks[tid]

            # send http request to clc to
            #  1. add a new image record, and set it properties
            #  2. delete transaction record
            clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
            payload = submitImageFinished(clcip, tid)

            logger.error("submitImageFinished with result = %s" % payload)
            payload = json.dumps(payload)
            ch.basic_publish(
                     exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=payload)
            ch.basic_ack(delivery_tag = method.delivery_tag)

            _tid = tid.split(':')
            dstimgid = _tid[1]

            if not amIclc():
                oldversionNo = ReadImageVersionFile(dstimgid)
                newversionNo = IncreaseImageVersion(oldversionNo)
                WriteImageVersionFile(dstimgid,newversionNo)
                logger.error("image %s version = %s" % (dstimgid, newversionNo))
        except Exception as e:
            logger.error("cc_rpc_handle_submit_success Exception Error Message : %s" % str(e))

    def cc_rpc_handle_image_running(self, ch, method, props, tid, paras):
        try:
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
        except Exception as e:
            logger.error("cc_rpc_handle_image_running Exception Error Message : %s" % str(e))

    def cc_rpc_handle_image_stopped(self, ch, method, props, tid, paras):
        try:
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
        except Exception as e:
            logger.error("cc_rpc_handle_image_stopped Exception Error Message : %s" % str(e))


def main():
    rpcserver = cc_rpcServer()
    rpcserver.run()

if __name__ == '__main__':
    main()