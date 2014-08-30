from luhyaapi.run4everProcess import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.rsyncWrapper import *
import pika, json, time

logger = getncdaemonlogger()

class downloadWorkerThread(threading.Thread):
    def __init__(self, dstip, tid):
        threading.Thread.__init__(self)

        self.dstip    = dstip
        self.tid      = tid
        retval = tid.split(':')
        self.srcimgid = retval[0]
        self.progress = 0

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
            logger.error(msg)
            self.progress = int(pct.split('%')[0])

        exit_code = rsync.getExitStatus()
        if exit_code == 0:
            self.progress = -100
        else:
            self.progress = exit_code
        logger.error("%s: download thread exit with code=%s", self.tid, exit_code)

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
        retvalue = "OK"

        while True:
            download_rpc = RpcClient(logger, self.ccip)
            response = download_rpc.call(cmd="image/download", paras=self.tid)
            response = json.loads(response)
            if response['progress'] < 0:
                if response['progress'] == -100:
                    response['progress'] = 50
                    self.forwardTaskStatus2CC(json.dumps(response))
                else:
                    retvalue = "FALURE"
                break
            else:
                response['progress'] = response['progress']/2.0
                self.forwardTaskStatus2CC(json.dumps(response))
                logger.error("downlaod from walrus: %s", response['progress'])
                time.sleep(1)

        return retvalue

    def forwardTaskStatus2CC(self, response):
        simple_send(logger, self.ccip, 'cc_status_queue', response)

    def downloadFromCC2NC(self):
        worker = downloadWorkerThread(self.ccip, self.tid)
        worker.start()

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "downloading",
                'progress'  : 0,
                'tid'       : self.tid,
                'errormsg'  : "",
        }

        while True:
            progress = worker.getprogress()
            if progress > 0:
                progress = 50 + progress / 2.5
                payload['progress'] = progress
                self.forwardTaskStatus2CC(json.dumps(payload))
                time.sleep(2)
            else:
                if progress < 0:
                    if progress == -100:
                        progress = 90
                        payload['progress'] = progress
                        self.forwardTaskStatus2CC(json.dumps(payload))
                    else:
                        logger.error("download from CC failed with error code = %s", progress)
                break;

        return "OK"

    def cloneImage(self):
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "downloading",
            'progress'  : 90,
            'tid'       : self.tid
        }

        if self.srcimgid != self.dstimgid:
            # call clone cmd
            time.sleep(5)
            payload['progress'] = 100
            self.forwardTaskStatus2CC(json.dumps(payload))
        else:
            payload['progress'] = 100
            self.forwardTaskStatus2CC(json.dumps(payload))

        payload['progress'] = -100
        self.forwardTaskStatus2CC(json.dumps(payload))
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
