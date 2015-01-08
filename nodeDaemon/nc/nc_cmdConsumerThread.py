from luhyaapi.run4everProcess import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.rsyncWrapper import *
from luhyaapi.vboxWrapper import *
from luhyaapi.clcAPIWrapper import *
import pika, json, time, shutil, os, commands

logger = getncdaemonlogger()

class prepareImageTaskThread(threading.Thread):
    def __init__(self, tid, runtime_option):
        threading.Thread.__init__(self)
        retval                  = tid.split(':')
        self.tid                = tid
        self.srcimgid           = retval[0]
        self.dstimgid           = retval[1]
        self.insid              = retval[2]
        self.runtime_option     = json.loads(runtime_option)
        self.ccip               = getccipbyconf()
        self.download_rpc       = RpcClient(logger, self.ccip)
        self.cc_img_info        = getImageVersionFromCC(self.ccip, self.srcimgid)
        self.nc_img_version, self.nc_img_size = getLocalImageInfo(self.srcimgid)
        self.nc_dbsize          = getLocalDatabaseInfo(self.srcimgid)
        logger.error('prepareImageTaskThread inited, tid=%s' % tid)

    def checkCLCandCCFile(self, paras):
        result = verify_clc_cc_image_info(self.ccip, self.srcimgid)

        if paras == 'luhya':
            if result['clc']['version'] == result['cc']['version'] and \
               result['clc']['size']    == result['cc']['size']:
                return 'NO'
            else:
                return "YES"

        if paras == 'db':
            if result['clc']['dbsize'] == result['cc']['dbsize']:
                return 'NO'
            else:
                return 'YES'

    # RPC call to ask CC download image from walrus
    def downloadFromWalrus2CC(self, data):
        logger.error('downloadFromWalrus2CC start ... ...')
        retvalue = "OK"

        needDownloading = self.checkCLCandCCFile(data['rsync'])
        if needDownloading == 'NO':
            response = {
                'type'      : 'taskstatus',
                'phase'     : "preparing",
                'state'     : 'downloading',
                'progress'  : 0,
                'tid'       : self.tid,
                'prompt'    : '',
                'errormsg'  : '',
                'failed'    : 0,
                'done'      : 1,
            }
            self.forwardTaskStatus2CC(json.dumps(response))
            logger.error('image in walrus info is SAME as that in cc.')
        else:
            while True:
                response = self.download_rpc.call(cmd=data['cmd'], tid=data['tid'], paras=data['rsync'])
                response = json.loads(response)

                if response['failed'] == 1:
                    logger.error(' ----- failed . ')
                    retvalue = "FALURE"
                    response['state'] = 'init'
                    self.forwardTaskStatus2CC(json.dumps(response))
                    break
                elif response['done'] == 1:
                    logger.error(' ----- done . ')
                    response['progress'] = 0
                    self.forwardTaskStatus2CC(json.dumps(response))
                    break
                else:
                    logger.error('progress = %s' % response['progress'])
                    self.forwardTaskStatus2CC(json.dumps(response))

                time.sleep(2)

        return retvalue

    def forwardTaskStatus2CC(self, response):
        simple_send(logger, self.ccip, 'cc_status_queue', response)

    def downloadFromCC2NC(self, data):
        logger.error('downloadFromCC2NC start ... ...')
        retvalue = "OK"

        payload = {
            'type'      : 'taskstatus',
            'phase'     : "preparing",
            'state'     : "downloading",
            'progress'  : 0,
            'tid'       : self.tid,
            'prompt'    : '',
            'errormsg'  : "",
            'failed'    : 0,
            'done'      : 0,
        }

        paras = data['rsync']
        if paras == 'luhya':
            prompt      = 'Downloading image file from CC to NC ... ...'
            source      = "rsync://%s/%s/%s" % (self.ccip, data['rsync'], self.srcimgid)
            destination = "/storage/images/"

            if self.cc_img_info['data']['version'] == self.nc_img_version and \
               self.cc_img_info['data']['size'] == self.nc_img_size:
                payload['progress'] = 0
                payload['done']     = 1
                self.forwardTaskStatus2CC(json.dumps(payload))
                logger.error("image in cc is SAME as that in nc. ")
                return retvalue
            else:
                payload['prompt'] = prompt

        if paras == 'db':
            prompt      = 'Downloading database file from CC to NC ... ...'
            source      = "rsync://%s/%s/%s" % (self.ccip, data['rsync'], self.srcimgid)
            destination = "/storage/space/database/images/"
            if self.cc_img_info['data']['dbsize'] == self.nc_dbsize:
                payload['progress'] = 0
                payload['done']     = 1
                self.forwardTaskStatus2CC(json.dumps(payload))
                logger.error("database in cc is SAME as that in nc. ")
                return retvalue
            else:
                payload['prompt'] = prompt

        worker = rsyncWorkerThread(logger, source, destination)
        worker.start()

        while True:
            payload['progress'] = worker.getprogress()
            payload['failed'] = worker.isFailed()
            payload['done'] = worker.isDone()
            if worker.isFailed():
                logger.error(' ----- failed . ')
                payload['failed'] = worker.isFailed()
                payload['errormsg'] = worker.getErrorMsg()
                payload['state'] = 'init'
                self.forwardTaskStatus2CC(json.dumps(payload))
                retvalue = "FALURE"
                break
            elif worker.isDone():
                logger.error(' ----- Done . ')
                payload['progress'] = 0
                self.forwardTaskStatus2CC(json.dumps(payload))
                break
            else:
                logger.error('progress = %s' % payload['progress'])
                self.forwardTaskStatus2CC(json.dumps(payload))

            time.sleep(2)

        return retvalue

    def cloneImage(self, data):
        logger.error('cloneImage start ... ...')
        retvalue = "OK"

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "preparing",
                'state'     : "cloning",
                'progress'  : 0,
                'tid'       : self.tid,
                'prompt'    : 'Cloning the file ... ...',
                'errormsg'  : "",
                'failed'    : 0,
                'done'      : 0,
        }

        dstfile  = None
        if data['rsync'] == 'luhya':
            srcfile  = "/storage/images/%s/machine"      % self.srcimgid
            dstfile  = "/storage/tmp/images/%s/machine"  % self.dstimgid
        if data['rsync'] == 'db':
            srcfile  = "/storage/space/database/images/%s/database" % self.srcimgid
            if self.insid.find('TMP') == 0:
                dstfile  = "/storage/space/database/images/%s/database" % self.dstimgid
            if self.insid.find('VS')  == 0:
                dstfile  = "/storage/space/database/instances/%s/database" % self.insid

        if self.srcimgid != self.dstimgid and dstfile != None :
            # call clone cmd
            cmd = 'vboxmanage closemedium disk %s --delete' % dstfile
            logger.error("cmd line = %s", cmd)
            pexpect.spawn(cmd)
            if os.path.exists(os.path.dirname(dstfile)):
                shutil.rmtree(os.path.dirname(dstfile))

            src_size = os.path.getsize(srcfile)

            cmd = "vboxmanage clonehd" + " " + srcfile + " " + dstfile
            logger.error("cmd line = %s", cmd)
            ratio = 0
            procid = pexpect.spawn(cmd)

            while procid.isalive():
                try:
                    dst_size = os.path.getsize(dstfile)
                except:
                    dst_size = 0

                ratio = int(dst_size * 100.0 / src_size)
                logger.error('current clone percentage is %d' % ratio)
                payload['progress'] = ratio
                self.forwardTaskStatus2CC(json.dumps(payload))
                time.sleep(2)

            if procid.status == 0:
                payload['progress'] = 100
                payload['done'] = 1
                logger.error('current clone percentage is done')
                self.forwardTaskStatus2CC(json.dumps(payload))
            else:
                logger.error(' ----- failed . ')
                retvalue = "FAILURE"
                payload['failed'] = 1
                payload['state']  = 'init'
                payload['errormsg'] = 'Failed in Cloning file.'
                self.forwardTaskStatus2CC(json.dumps(payload))

        return retvalue

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

        if done_1 == True:
            if self.runtime_option['usage'] == 'server': # desktop, server, app
                data['rsync'] = 'db'
                if self.downloadFromWalrus2CC(data) == "OK":
                    if self.cloneImage(data) == "OK":
                        done_2 = True
            else:
                done_2 = True

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "preparing",
                'state'     : 'done',
		'progress'  :  0,
                'tid'       : self.tid,
                'prompt'    : '',
                'errormsg'  : '',
                'failed'    : 0,
        }

        if done_1 == False or done_2 == False:
            logger.error('send cmd image/prepare/failure ')
            self.download_rpc.call(cmd="image/prepare/failure", tid=data['tid'], paras=data['rsync'])
            payload['state'] = 'init'
            payload['failed'] = 1
            payload = json.dumps(payload)
            self.forwardTaskStatus2CC(payload)
        else:
            logger.error('send cmd image/prepare/success ')
            self.download_rpc.call(cmd="image/prepare/success", tid=data['tid'], paras=data['rsync'])
            payload = json.dumps(payload)
            self.forwardTaskStatus2CC(payload)

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
        if self.dstimgid != self.srcimgid:
            self.root_dir = "/storage/tmp/images/"
        else:
            self.root_dir = "/storage/images/"

    # RPC call to ask CC download image from walrus
    def submitFromCC2Walrus(self, data):
        logger.error('submitFromCC2Walrus start ... ...')
        retvalue = "OK"

        while True:
            response = self.download_rpc.call(cmd=data['cmd'], tid=data['tid'], paras=data['rsync'])
            response = json.loads(response)

            if response['failed'] == 1:
                logger.error(' ----- failed . ')
                retvalue = "FALURE"
                self.forwardTaskStatus2CC(json.dumps(response))
                break
            if response['done'] == 1:
                logger.error(' ----- done . ')
                response['progress'] = 0
                self.forwardTaskStatus2CC(json.dumps(response))
                break
            else:
                logger.error('progress = %s' % response['progress'])
                self.forwardTaskStatus2CC(json.dumps(response))

            time.sleep(2)

        return retvalue

    def forwardTaskStatus2CC(self, response):
        simple_send(logger, self.ccip, 'cc_status_queue', response)

    def submitFromNC2CC(self, data):
        logger.error('submitFromNC2CC start ... ...')
        retvalue = "OK"

        paras = data['rsync']
        prompt = 'Uploading file from NC to CC ... ...'
        if paras == 'luhya':
            prompt      = 'Uploading image file from NC to CC ... ...'
            source      = self.root_dir + self.dstimgid
            destination = "rsync://%s/%s/" % (self.ccip, data['rsync'])
        if paras == 'db':
            prompt      = 'Uploading database file from NC to CC ... ...'
            source      = '/storage/space/database/' + self.dstimgid
            destination = "rsync://%s/%s/" % (self.ccip, data['rsync'])

        worker = rsyncWorkerThread(logger, source, destination)
        worker.start()

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "submitting",
                'state'     : 'uploading',
                'progress'  : 0,
                'tid'       : self.tid,
                'prompt'    : prompt,
                'errormsg'  : "",
                'failed'    : 0,
                'done'      : 0,
        }

        while True:
            payload['progress'] = worker.getprogress()
            payload['failed'] = worker.isFailed()
            payload['done'] = worker.isDone()
            if worker.isFailed():
                logger.error(' ----- failed . ')
                payload['failed'] = worker.isFailed()
                payload['errormsg'] = worker.getErrorMsg()
                payload['state'] = 'init'
                self.forwardTaskStatus2CC(json.dumps(payload))
                retvalue = "FALURE"
                break
            elif worker.isDone():
                logger.error(' ----- Done . ')
                payload['progress'] = 0
                self.forwardTaskStatus2CC(json.dumps(payload))
                break
            else:
                logger.error('progress = %s' % payload['progress'])
                self.forwardTaskStatus2CC(json.dumps(payload))
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
        logger.error(' -------- task_finished')
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
            WriteImageVersionFile(self.dstimgid, newversionNo)

    def run(self):
        done_1 = False
        done_2 = False

        data = {}
        data['cmd']     = 'image/submit'
        data['tid']     =  self.tid
        data['rsync']   = 'luhya'

        self.delete_snapshort()

        if self.submitFromNC2CC(data) == "OK":
            if self.submitFromCC2Walrus(data) == "OK":
                done_1 = True

        if done_1 == True:
            if self.runtime_option['usage'] == 'server':
                data['rsync'] = 'db'
                if self.submitFromCC2Walrus(data) == "OK":
                    done_2 = True
            else:
                done_2 = True

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "submitting",
                'state'     : 'done',
		'progress'  :  0,
                'tid'       : self.tid,
                'prompt'    : '',
                'errormsg'  : '',
                'failed'    : 0,
        }

        if done_1 == False or done_2 == False:
            logger.error('send cmd image/submit/failure ')
            self.download_rpc.call(cmd="image/submit/failure", tid=data['tid'], paras=data['rsync'])
            # send mssage to notify prepare is done
            payload['state'] = 'init'
            payload['failed'] = 1
            payload = json.dumps(payload)
            self.forwardTaskStatus2CC(payload)

            self.download_rpc.call(cmd="image/submit/failure", tid=data['tid'], paras=data['rsync'])
        else:
            payload = json.dumps(payload)
            self.forwardTaskStatus2CC(payload)

            logger.error('send cmd image/submit/success whith payload=%s' % payload)
            self.download_rpc.call(cmd="image/submit/success", tid=data['tid'], paras=data['rsync'])

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

    # need to consider vd & vs creation
    # c: d: e: f:

    def createvm(self):
        flag = True
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "editing",
            'state'     : 'booting',
            'tid'       : self.tid,
            'errormsg'  : '',
            'failed'    : 0,
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

                    # add disks
                    index = 0
                    for disk in self.runtime_option['disks']:
                        ret, err = vboxmgr.attachHDD(self.runtime_option['disk_type'], disk['mtype'], disk['file'])
                        logger.error("--- --- --- vboxmgr.attachHDD %s, error=%s" % (disk['file'], err))
                        if index == 0 and self.runtime_option['run_with_snapshot'] == 1:
                            snapshot_name = "thomas"
                            if not vboxmgr.isSnapshotExist(snapshot_name):
                                ret, err = vboxmgr.take_snapshot(snapshot_name)
                                logger.error("--- --- --- vboxmgr.take_snapshot, error=%s" % err)
                        index = index + 1

                    # add folders
                    for folder in self.runtime_option['folders']:
                        ret, err = vboxmgr.attachSharedFolder(folder)
                        logger.error("--- --- --- vboxmgr.attachSharedFolder %s, error=%s" % (folder , err))

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

                    ret, err = vboxmgr.unregisterVM()
                    ret, err = vboxmgr.registerVM()
                except Exception as e:
                    ret, err = vboxmgr.unregisterVM()
                    vboxmgr.deleteVMConfigFile()
                    flag = False
                    payload['failed']   = 1
                    payload['state']    = 'stopped'
                    payload['errormsg'] = e.message
                    simple_send(logger, self.ccip, 'cc_status_queue', json.dumps(payload))

        return flag

    def runvm(self):
        flag = True
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "editing",
            'state'     : 'running',
            'tid'       : self.tid,
            'errormsg'  : '',
            'failed'    : 0,
        }

        vboxmgr = self.vboxmgr
        try:
            if not vboxmgr.isVMRunning():
                ret, err = vboxmgr.runVM(headless=True)
                logger.error("--- --- --- vboxmgr.runVM, error=%s" % err)
                if err != "":
                    flag = False
                    payload['failed'] = 1
                    payload['errormsg'] = err
                    payload['state'] = 'stopped'

        except Exception as e:
            flag = False
            payload['failed'] = 1
            payload['state'] = 'stopped'
            payload['errormsg'] = e.message

        simple_send(logger, self.ccip, 'cc_status_queue', json.dumps(payload))
        return flag

    def run(self):
        done_1 = False
        done_2 = False

        disks = []

        if self.runtime_option['usage'] == 'desktop':
            if self.srcimgid == self.dstimgid :
                # modify desktop
                pass
            else:
                # build new desktop
                pass
        if self.runtime_option['usage'] == 'server':
            if self.srcimgid == self.dstimgid :
                # modify server
                pass
            else:
                # build new server
                pass

        if self.createvm(disks) == True:
            done_1 = True
            if self.runvm() == True:
                done_2 = True

        if done_1 == False or done_2 == False:
            self.rpcClient.call(cmd="image/edit/stopped", tid=self.tid, paras='')
        else:
            self.rpcClient.call(cmd="image/edit/running", tid=self.tid, paras='')

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

def nc_image_stop_handle(tid, runtime_option):
    logger.error("--- --- --- nc_image_stop_handle")

    retval   = tid.split(':')
    srcimgid = retval[0]
    dstimgid = retval[1]
    insid    = retval[2]

    cmd = "vboxmanage controlvm %s poweroff" % insid
    out = commands.getoutput(cmd)

    payload = {
            'type'      : 'taskstatus',
            'phase'     : "editing",
            'state'     : 'stopped',
            'progress'  : 0,
            'tid'       : tid,
            'errormsg'  : '',
            'failed'    : 0
    }

    ccip = getccipbyconf()
    simple_send(logger, ccip, 'cc_status_queue', json.dumps(payload))

    # need to update nc's status at once
    update_nc_running_status()

    # process for different type instance
    if srcimgid != dstimgid:
        rootdir = "/storage/tmp"
    else:
        rootdir = "/storage"

    vboxmgr = vboxWrapper(dstimgid, insid, rootdir)

    # build/modify insid is TMPxxxxx, when stopped, do nothing else
    if insid.find('TMP') == 0:
        pass

    # running vd   insid is VDxxxx,   when stopped, delete all except image file
    if insid.find('VD') == 0:
        vboxmgr.unregisterVM()
        vboxmgr.deleteVMConfigFile()

    # running vs   insid is VSxxxx,   when stopped, delete all except image file
    if insid.find('VS') == 0:
        vboxmgr.unregisterVM()
        vboxmgr.deleteVMConfigFile()

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
