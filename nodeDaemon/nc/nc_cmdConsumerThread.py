from luhyaapi.run4everProcess import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.vboxWrapper import *
from luhyaapi.clcAPIWrapper import *
import pika, json, time, shutil, os, commands

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
    def __init__(self, tid, runtime_option):
        threading.Thread.__init__(self)
        retval = tid.split(':')
        self.tid      = tid
        self.srcimgid = retval[0]
        self.dstimgid = retval[1]
        self.runtime_option = json.loads(runtime_option)
        self.ccip     = getccipbyconf()
        self.download_rpc = RpcClient(logger, self.ccip)

    # RPC call to ask CC download image from walrus
    def downloadFromWalrus2CC(self, data):
        retvalue = "OK"

        while True:
            response = self.download_rpc.call(cmd=data['cmd'], tid=data['tid'], paras=data['rsync'])
            response = json.loads(response)

            if response['failed'] == 1:
                retvalue = "FALURE"
                self.forwardTaskStatus2CC(json.dumps(response))
                break
            else:
                self.forwardTaskStatus2CC(json.dumps(response))
                if response['progress'] == 100:
                    break

            time.sleep(2)

        return retvalue

    def forwardTaskStatus2CC(self, response):
        simple_send(logger, self.ccip, 'cc_status_queue', response)

    def downloadFromCC2NC(self, data):
        retvalue = "OK"

        paras = data['rsync']
        prompt = 'Downloading file from Walrus to CC ... ...'
        if paras == 'luhya':
            prompt = 'Downloading image file from Walrus to CC ... ...'
        if paras == 'db':
            prompt = 'Downloading database file from Walrus to CC ... ...'

        worker = downloadWorkerThread(self.ccip, self.tid, paras)
        worker.start()

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "preparing",
                'state'     : "downloading",
                'progress'  : 0,
                'tid'       : self.tid,
                'prompt'    : prompt,
                'errormsg'  : "",
                'failed'    : 0
        }

        while True:
            payload['progress'] = worker.getprogress()
            payload['failed']   = worker.isFailed()
            if worker.isFailed():
                payload['failed']   = worker.isFailed()
                payload['errormsg'] = worker.getErrorMsg()
                payload['state']    = 'init'
                self.forwardTaskStatus2CC(json.dumps(payload))
                retvalue = "FALURE"
                break
            else:
                self.forwardTaskStatus2CC(json.dumps(payload))
                if payload['progress'] == 100:
                    break

            time.sleep(2)

        return retvalue

    def cloneImage(self, data):
        retvalue = "OK"

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "prepare",
                'state'     : "clone",
                'progress'  : 0,
                'tid'       : self.tid,
                'prompt'    : '',
                'errormsg'  : "",
                'failed'    : 0,
        }

        if self.srcimgid == self.dstimgid:
            payload['progress'] = 100
            self.forwardTaskStatus2CC(json.dumps(payload))
        else:
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
                payload['progress'] = 100
                self.forwardTaskStatus2CC(json.dumps(payload))


        self.forwardTaskStatus2CC(json.dumps(payload))


        return "OK"

    def run(self):
        done_1 = False
        done_2 = False

        data = {}
        data['cmd']     = 'image/prepare'
        data['tid']     =  self.tid
        data['rsync']   = 'luhya'

        if self.downloadFromWalrus2CC(data) == "OK":
            if self.downloadFromCC2NC(data) == "OK":
                if self.cloneImage(data) == "OK":
                    done_1 = True

        if self.runtime_option['usage'] != 'desktop': # desktop, server, app
            data['rsync'] = 'db'
            if self.downloadFromWalrus2CC(data) == "OK":
                done_2 = True
        else:
            done_2 = True

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "preparing",
                'state'     : 'done',
                'tid'       : self.tid,
                'prompt'    : '',
                'errormsg'  : '',
                'failed'    : 0,
        }

        if done_1 == False or done_2 == False:
            self.download_rpc.call(cmd="image/prepare/failure", tid=data['tid'], paras=data['rsync'])
            # send mssage to notify prepare is done
            payload['state']    = 'init'
            payload['failed']   = 1
        else:
            self.download_rpc.call(cmd="image/prepare/success", tid=data['tid'], paras=data['rsync'])

        payload = json.dumps(payload)
        self.forwardTaskStatus2CC(payload)


class submitWorkerThread(threading.Thread):
    def __init__(self, dstip, tid):
        threading.Thread.__init__(self)

        self.dstip    = dstip
        self.tid      = tid
        retval = tid.split(':')
        self.srcimgid = retval[0]
        self.dstimgid = retval[1]
        self.progress = 0
        self.failed   = 0

    def isFailed(self):
        return self.failed

    def getprogress(self):
        return self.progress

    def run(self):
        logger.error("enter into submitWorkerThread run()")
        self.progress = 0

        if self.dstimgid != self.srcimgid:
            root_dir = "/storage/tmp/images/"
        else:
            root_dir = "/storage/images/"
        source= root_dir + self.dstimgid
        destination = "rsync://%s/luhya/" % (self.dstip)

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
        logger.error("%s: submitting thread exit with code=%s", self.tid, exit_code)


class SubmitImageTaskThread(threading.Thread):
    def __init__(self, tid, runtime_option):
        threading.Thread.__init__(self)
        retval = tid.split(':')
        self.tid      = tid
        self.srcimgid = retval[0]
        self.dstimgid = retval[1]
        self.insid    = retval[2]
        self.ccip     = getccipbyconf()
        self.runtime_option = json.loads(runtime_option)
        self.download_rpc = RpcClient(logger, self.ccip)

    # RPC call to ask CC download image from walrus
    def submitFromCC2Walrus(self):
        retvalue = "OK"

        while True:
            response = self.download_rpc.call(cmd="image/submit", paras=self.tid)
            response = json.loads(response)
            if response['failed'] == 1:
                retvalue = "FALURE"
                self.forwardTaskStatus2CC(json.dumps(response))
                self.download_rpc.call(cmd="image/submit/failure", paras=self.tid)
                break
            else:
                if response['progress'] < 0:
                    if response['progress'] == -100:
                        response['progress'] = 100
                        self.forwardTaskStatus2CC(json.dumps(response))
                    else:
                        retvalue = "FALURE"
                        self.download_rpc.call(cmd="image/submit/failure", paras=self.tid)
                    break
                else:
                    response['progress'] = 50 + response['progress']/2.0
                    self.forwardTaskStatus2CC(json.dumps(response))
                    logger.error("submit to walrus: %s", response['progress'])
                    time.sleep(2)

        return retvalue

    def forwardTaskStatus2CC(self, response):
        simple_send(logger, self.ccip, 'cc_status_queue', response)

    def submitFromNC2CC(self):
        retvalue = "OK"

        worker = submitWorkerThread(self.ccip, self.tid)
        worker.start()

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "submitting",
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
                self.download_rpc.call(cmd="image/submit/failure", paras=self.tid)
                break
            else:
                if progress < 0:
                    if progress == -100:
                        progress = 50
                        payload['progress'] = progress
                        self.forwardTaskStatus2CC(json.dumps(payload))
                    else:
                        retvalue = "FALURE"
                        self.download_rpc.call(cmd="image/submit/failure", paras=self.tid)
                    break;
                else:
                    progress = progress / 2.0
                    payload['progress'] = progress
                    self.forwardTaskStatus2CC(json.dumps(payload))
                    logger.error("submit to cc: %s", payload['progress'])
                    time.sleep(2)

        return retvalue

    def delete_snapshort(self):
        if self.srcimgid != self.dstimgid:
            rootdir = "/storage/tmp"
        else:
            rootdir = "/storage"
        self.vboxmgr = vboxWrapper(self.dstimgid, self.insid, rootdir)
        snapshot_name = "thomas"
        if self.vboxmgr.isSnapshotExist(snapshot_name):
            out, err = self.vboxmgr.delete_snapshot(snapshot_name)
            logger.error("luhya: delete snapshort with result - out=%s - err=%s", out, err)

    def task_finished(self):
        response = self.download_rpc.call(cmd="image/submit/success", paras=self.tid)
        response = json.loads(response)

        if self.srcimgid != self.dstimgid:
            self.vboxmgr.unregisterVM(delete=True)
            self.vboxmgr.deleteVMConfigFile()

            rootdir = "/storage/tmp"
            if os.path.exists(rootdir + "/images/" + self.dstimgid):
                shutil.rmtree(rootdir + "/images/" + self.dstimgid)
        else:
            self.vboxmgr.unregisterVM()
            self.vboxmgr.deleteVMConfigFile()

            oldversionNo = ReadImageVersionFile(self.dstimgid)
            newversionNo = IncreaseImageVersion(oldversionNo)
            WriteImageVersionFile(self.dstimgid,newversionNo)

    def run(self):
        self.delete_snapshort()
        if self.submitFromNC2CC() == "OK":
            if self.submitFromCC2Walrus() == "OK":
                self.task_finished()

def nc_image_prepare_handle(tid, runtime_option):
    logger.error("--- --- --- nc_image_prepare_handle")
    worker = prepareImageTaskThread(tid, runtime_option)
    worker.start()
    return worker

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

        self.rpcClient = RpcClient(logger, self.ccip)

    def createvm(self):
        flag = True
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "editing",
            'tid'       : self.tid,
            'errormsg'  : '',
            'vmstatus'  : 'init',
            'failed'    : 0,
            'url'       : '',
        }

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
                    logger.error("--- --- --- vboxmgr.createVM, error=%s" % err)
                    ret, err = vboxmgr.registerVM()
                    logger.error("--- --- --- vboxmgr.registerVM, error=%s" % err)
                    if self.runtime_option['disk_type'] == 'IDE':
                        ret, err = vboxmgr.addCtrl(" --name IDE --add ide ")
                    else:
                        ret, err = vboxmgr.addCtrl(" --name SATA --add sata ")
                        ret, err = vboxmgr.addCtrl(" --name IDE --add ide ")
                    logger.error("--- --- --- vboxmgr.addCtrl, error=%s" % err)

                    ret, err = vboxmgr.attachHDD_c(storageCtl = self.runtime_option['disk_type'])
                    logger.error("--- --- --- vboxmgr.attachHDD_c")
                    if self.runtime_option['run_with_snapshot'] == 1:
                        snapshot_name = "thomas"
                        if not vboxmgr.isSnapshotExist(snapshot_name):
                            ret, err = vboxmgr.take_snapshot(snapshot_name)
                            logger.error("--- --- --- vboxmgr.take_snapshot, error=%s" % err)

                    ret, err = vboxmgr.attachHDD_shared_d(storageCtl = self.runtime_option['disk_type'])
                    logger.error("--- --- --- vboxmgr.attachHDD_shared_d, error=%s" % err)

                    # in server side, the SharedFolder is by default
                    # need to mount cc's /storage/data to each NC
                    ret, err = vboxmgr.attachSharedFolder(path="/storage/data")
                    logger.error("--- --- --- vboxmgr.attachSharedFolder, error=%s" % err)

                    # in servere side, each VM has 4G mem
                    _cpus    = self.runtime_option['cpus']
                    _memory  = self.runtime_option['memory'] * 1024
                    if self.runtime_option['usage'] == 'desktop':
                        _network_para = " --nic1 nat  --nictype1 %s " % self.runtime_option['networkcards'][0]['nic_type']
                    else:
                        _network_para = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 %s " % self.runtime_option['networkcards'][0]['nic_type']
                    ostypepara_value = _network_para +  self.runtime_option['audio_para']
                    ret, err = vboxmgr.modifyVM(osTypeparam=ostypepara_value, cpus = _cpus, mem=_memory, )
                    logger.error("--- --- --- vboxmgr.modifyVM, error=%s" % err)

                    # in server side, configure headless property
                    portNum = self.runtime_option['rdp_port']
                    ret, err = vboxmgr.addHeadlessProperty(port=portNum)
                    logger.error("--- --- --- vboxmgr.addHeadlessProperty, error=%s" % err)
                except Exception as e:
                    ret, err = vboxmgr.unregisterVM()
                    vboxmgr.deleteVMConfigFile()
                    flag = False
                    payload['failed'] = 1
                    payload['errormsg'] = e.message
                    simple_send(logger, self.ccip, 'cc_status_queue', json.dumps(payload))


                ret, err = vboxmgr.unregisterVM()
                ret, err = vboxmgr.registerVM()

        return flag

    def runvm(self):
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "editing",
            'tid'       : self.tid,
            'errormsg'  : '',
            'vmstatus'  : 'running',
            'failed'    : 0,
            'url'       : '',
        }

        vboxmgr = self.vboxmgr
        try:
            if not vboxmgr.isVMRunning():
                ret, err = vboxmgr.runVM(headless=True)
                logger.error("--- --- --- vboxmgr.runVM, error=%s" % err)
                if err != "":
                    payload['failed'] = 1
                    payload['errormsg'] = err
                    payload['vmstatus'] = 'stopped'
                    self.rpcClient.call(cmd="image/edit/stopped", paras=self.tid)
                else:
                    self.rpcClient.call(cmd="image/edit/running", paras=self.tid)
        except Exception as e:
            payload['failed'] = 1
            payload['vmstatus'] = 'stopped'
            payload['errormsg'] = e.message
            self.rpcClient.call(cmd="image/edit/stopped", paras=self.tid)

        simple_send(logger, self.ccip, 'cc_status_queue', json.dumps(payload))



    def run(self):
        if self.createvm():
            self.runvm()

        # need to update nc's status at once
        update_nc_running_status()

def update_nc_running_status():
    payload = { }
    payload['type']             = 'nodestatus'
    payload['service_data']     = getServiceStatus('nc')
    payload['hardware_data']    = getHostHardware()
    payload['net_data']         = getHostNetInfo()
    payload['vm_data']          = getVMlist()

    payload['nid']              = "nc#" + payload['net_data']['mac0'] + "#status"

    ccip = getccipbyconf()
    simple_send(logger, ccip, 'cc_status_queue', json.dumps(payload))

def nc_image_run_handle(tid, runtime_option):
    logger.error("--- --- --- nc_image_run_handle")

    worker = runImageTaskThread(tid, runtime_option)
    worker.start()
    pass

def PoweroffVM(insID):
    cmd = "vboxmanage controlvm %s poweroff" % insID
    out = commands.getoutput(cmd)

def nc_image_stop_handle(tid, runtime_option):
    logger.error("--- --- --- nc_image_stop_handle")

    retval   = tid.split(':')
    srcimgid = retval[0]
    dstimgid = retval[1]
    insid    = retval[2]
    PoweroffVM(insid)

    payload = {
            'type'      : 'taskstatus',
            'phase'     : "editing",
            'progress'  : 0,
            'tid'       : tid,
            'errormsg'  : '',
            'vmstatus'  : 'stopped',
            'failed'    : 0
    }

    ccip = getccipbyconf()
    simple_send(logger, ccip, 'cc_status_queue', json.dumps(payload))

    # need to update nc's status at once
    update_nc_running_status()

def nc_image_submit_handle(tid, runtime_option):
    logger.error("--- --- --- nc_image_submit_handle")

    worker = SubmitImageTaskThread(tid, runtime_option)
    worker.start()
    return worker


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
                nc_cmd_handlers[message['op']](message['tid'], message['runtime_option'])
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
