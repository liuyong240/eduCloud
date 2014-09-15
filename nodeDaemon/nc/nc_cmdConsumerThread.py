from luhyaapi.run4everProcess import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.vboxWrapper import *
from luhyaapi.clcAPIWrapper import *
import pika, json, time, shutil, os

logger = getncdaemonlogger()

class downloadWorkerThread(threading.Thread):
    def __init__(self, dstip, tid):
        threading.Thread.__init__(self)

        self.dstip    = dstip
        self.tid      = tid
        retval = tid.split(':')
        self.srcimgid = retval[0]
        self.progress = 0
        self.failed   = 0

    def isFailed(self):
        return self.failed

    def getprogress(self):
        return self.progress

    def isSameImageVersionAsServers(self):
        cc_ver  = ReadImageVersionFile(self.srcimgid)
        imginfo = getImageVersionFromCC(self.dstip, self.srcimgid)
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
                logger.error(msg)
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
            response = download_rpc.call(cmd="image/prepare", paras=self.tid)
            response = json.loads(response)
            if response['failed'] == 1:
                retvalue = "FALURE"
                self.forwardTaskStatus2CC(json.dumps(response))
                break
            else:
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
                    time.sleep(2)

        return retvalue

    def forwardTaskStatus2CC(self, response):
        simple_send(logger, self.ccip, 'cc_status_queue', response)

    def downloadFromCC2NC(self):
        retvalue = "OK"

        worker = downloadWorkerThread(self.ccip, self.tid)
        worker.start()

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "prepare",
                'progress'  : 0,
                'tid'       : self.tid,
                'errormsg'  : "",
                'failed'    : 0
        }

        while True:
            progress = worker.getprogress()
            payload['failed']   = worker.isFailed()
            if worker.isFailed():
                self.forwardTaskStatus2CC(json.dumps(payload))
                retvalue = "FALURE"
                break
            else:
                if progress < 0:
                    if progress == -100:
                        progress = 90
                        payload['progress'] = progress
                        self.forwardTaskStatus2CC(json.dumps(payload))
                    else:
                        retvalue = "FALURE"
                    break;
                else:
                    progress = 50 + progress / 2.5
                    payload['progress'] = progress
                    self.forwardTaskStatus2CC(json.dumps(payload))
                    logger.error("downlaod from cc: %s", payload['progress'])
                    time.sleep(2)

        return retvalue

    def cloneImage(self):
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "cloning",
            'progress'  : 90,
            'tid'       : self.tid
        }

        if self.srcimgid != self.dstimgid:
            # call clone cmd
            srcfile  = "/storage/images/"      + self.srcimgid + "/machine"
            dstfile  = "/storage/tmp/images/"  + self.dstimgid + "/machine"

            if os.path.exists(dstfile):
                shutil.rmtree("/storage/tmp/images/" + self.dstimgid)

            dest_size = 0
            src_size = os.path.getsize(srcfile)

            cmd = "vboxmanage clonehd" + " " + srcfile + " " + dstfile
            logger.info("cmd line = %s", cmd)
            ratio = 0
            procid = pexpect.spawn(cmd)

            while procid.isalive():
                time.sleep(1)
                try:
                    dst_size = os.path.getsize(dstfile)
                except:
                    dst_size = 0

                ratio = int(dst_size * 100.0 / src_size)
                logger.info('current clone percentage is %d' % ratio)
                payload['progress'] = ratio / 10.0 + 90
                self.forwardTaskStatus2CC(json.dumps(payload))

            if procid.status == 0:
                payload['progress'] = 100
                self.forwardTaskStatus2CC(json.dumps(payload))
            else:
                payload['progress'] = procid.status
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

def nc_image_prepare_handle(tid):
    worker = prepareImageTaskThread(tid)
    worker.start()
    return worker

'''
runtime_options
{
    ostype:
    usage:
    memory:
    cpus:
    nic_type:
    disk_type:
    audio_para:

    portNum:
    publicIP:
    privateIP:
    mac:
}
'''
class runImageTaskThread(threading.Thread):
    def __init__(self, tid, runtime_option):
        threading.Thread.__init__(self)

        self.ccip     = getccipbyconf()

        retval = tid.split(':')
        self.tid      = tid
        self.srcimgid = retval[0]
        self.dstimgid = retval[1]
        self.insid    = retval[2]
        self.runtime_option = json.loads(runtime_option)

    def createvm(self):
        flag = False
        if self.srcimgid != self.dstimgid:
            rootdir = "/storage/tmp"
        else:
            rootdir = "/storage"

        self.vboxmgr = vboxWrapper(self.dstimgid, self.insid, rootdir)
        vboxmgr = self.vboxmgr

        # register VM
        if not vboxmgr.isVMRegistered():
            if vboxmgr.isVMRegisteredBefore():
                ret, err = vboxmgr.registerVM()
            else:
                try:
                    ostype_value = self.runtime_option['ostype']
                    ret, err = vboxmgr.createVM(ostype=ostype_value)
                    ret, err = vboxmgr.registerVM()
                    if self.runtime_option['disk_type'] == 'IDE':
                        ret, err = vboxmgr.addCtrl(" --name IDE --add ide ")
                    else:
                        ret, err = vboxmgr.addCtrl(" --name SATA --add sata ")
                        ret, err = vboxmgr.addCtrl(" --name IDE --add ide ")

                    ret, err = vboxmgr.attachHDD_c(storageCtl = self.runtime_option['disk_type'])

                    if self.runtime_option['run_with_snapshot'] == 1:
                        snapshot_name = "thomas"
                        if not vboxmgr.isSnapshotExist(snapshot_name):
                            ret, err = vboxmgr.take_snapshot(snapshot_name)

                    ret, err = vboxmgr.attachHDD_shared_d(storageCtl = self.runtime_option['disk_type'])

                    # in server side, the SharedFolder is by default
                    # need to mount cc's /storage/data to each NC
                    ret, err = vboxmgr.attachSharedFolder(path="/storage/data")

                    # in servere side, each VM has 4G mem
                    _cpus    = self.runtime_option['cpus']
                    _memory  = self.runtime_option['memory']
                    if self.runtime_option['usage'] == 'desktop':
                        _network_para = " --nic1 nat  --nictype1 %s " % self.runtime_option['netwowrkcards'][0]['nic_type']
                    else:
                        _network_para = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 %s " % self.runtime_option['netwowrkcards'][0]['nic_type']
                    ostypepara_value = _network_para +  self.runtime_option['audio_para']
                    ret, err = vboxmgr.modifyVM(osTypeparam=ostypepara_value, cpus = _cpus, mem=_memory, )

                    # in server side, configure headless property
                    portNum = self.runtime_option['rdp_port']
                    ret, err = vboxmgr.addHeadlessProperty(port=portNum)
                except:
                    ret, err = vboxmgr.unregisterVM()
                    vboxmgr.deleteVMConfigFile()
                    return

                ret, err = vboxmgr.unregisterVM()
                ret, err = vboxmgr.registerVM()

    def runvm(self):
        pass

    def run(self):
        if self.createvm():
            self.runvm()


def nc_image_run_handle(tid, runtime_option):
    worker = runImageTaskThread(tid, runtime_option)
    worker.start()
    pass

def nc_image_stop_handle(tid):
    pass

def nc_image_submit_handle(tid):
    pass


nc_cmd_handlers = {
    'image/prepare'     : nc_image_prepare_handle,
    'image/run'         : nc_image_run_handle,
    'image/stop'        : nc_image_stop_handle,
    'image/submit'      : nc_image_submit_handle,
}

class nc_cmdConsumerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)
        self.ccip = getccipbyconf()

    def cmdHandle(self, ch, method, properties, body):
        logger.error(" get command = %s" %  body)
        message = json.loads(body)
        if  message['op'] in  nc_cmd_handlers and nc_cmd_handlers[message['op']] != None:
            if message['op'] == "image/run":
                nc_image_run_handle(message['paras'], message['runtime_option'])
            else:
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
