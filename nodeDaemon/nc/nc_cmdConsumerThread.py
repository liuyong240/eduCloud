from luhyaapi.run4everProcess import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.rsyncWrapper import *
import pika, json, time

logger = getncdaemonlogger()

class prepareImageTaskThread(threading.Thread):
    def __init__(self, tid):
        threading.Thread.__init__(self)
        retval = tid.split(':')
        self.tid      = tid
        self.srcimgid = retval[0]
        self.dstimgid = retval[1]
        self.ccip     = getccipbyconf()

    # RPC call to ask CC download image from walrus
    def downloadFromWalrus2CC(self):
        while True:
            download_rpc = RpcClient(logger, self.ccip)
            response = download_rpc.call(cmd="image/download", paras=self.tid)
            self.forwardTaskStatus2CC(response)

            response = json.loads(response)
            logger.error("rpc call return value: %s-%s" % (response['tid'], response['progress']))
            if response['progress'] < 0:
                break
            else:
                time.sleep(1)

        return 'OK'

    def forwardTaskStatus2CC(self, response):
        simple_send(logger, self.ccip, 'cc_status_queue', response)

    def downloadFromCC2NC(self):
        source = "rsync://%s/luhya/%s" % (self.ccip, self.srcimgid)
        destination = "/storage/images/"
        rsync = rsyncWrapper(source, destination)
        rsync.startRsync()

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "downloading",
                'progress'  : 0,
                'tid'       : self.tid
        }

        while rsync.isRsyncLive():
            tmpfilesize, pct, bitrate, remain = rsync.getProgress()
            msg = "%s  %s %s %s" % (tmpfilesize, pct, bitrate, remain)
            logger.error(msg)
            self.progress = int(pct.split('%')[0])

            payload['progress'] = self.progress
            message = json.dumps(payload)
            self.forwardTaskStatus2CC(message)


        exit_code = rsync.getExitStatus()
        logger.error("%s: download thread exit with code=%s", self.tid, exit_code)

        return "OK"

    def cloneImage(self):
        if self.srcimgid != self.dstimgid:
            # call clone cmd
            return "OK"

    def run(self):
        if self.downloadFromWalrus2CC() == "OK":
            if self.downloadFromCC2NC() == "OK":
                self.cloneImage()

def nc_image_create_handle(tid):
    worker = prepareImageTaskThread(tid)
    worker.start()
    return worker

def nc_image_modify_handle(tid):
    time.sleep(100)

nc_cmd_handlers = {
    'image/create'      : nc_image_create_handle,
    'image/modify'      : nc_image_modify_handle,
}

class nc_cmdConsumerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)
        self.ccip = getccipbyconf()

    def cmdHandle(self, ch, method, properties, body):
        logger.error(" get coommand = %s" %  body)
        message = json.loads(body)
        if  message['op'] in  nc_cmd_handlers and nc_cmd_handlers[message['op']] != None:
            nc_cmd_handlers[message['op']](message['paras'])
        else:
            logger.error("unknow cmd : %s", message['op'])

    def run4ever(self):
        connection = getConnection(self.ccip)
        channel = connection.channel()

        channel.exchange_declare(exchange='nc_cmd',
                                 type='direct')

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        ip0 = getHostNetInfo()['ip0']

        channel.queue_bind(exchange='nc_cmd',
                           queue=queue_name,
                           routing_key=ip0)

        channel.basic_consume(self.cmdHandle,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()
