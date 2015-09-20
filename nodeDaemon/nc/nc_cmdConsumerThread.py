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
        logger.error('prepareImageTaskThread inited, tid=%s' % tid)

    def checkCLCandCCFile(self, paras):
        logger.error("Enter checkCLCandCCFile() ... ... ")
        result = verify_clc_cc_image_info(self.ccip, self.tid)
        logger.error("clc vs cc image info = %s" % json.dumps(result))

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
        logger.error("needDownloading = %s" % needDownloading)
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
                logger.error("self.download_rpc.call return = %s" % response)
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
        logger.error('Enter downloadFromCC2NC  ... ...')
        locale_string = getlocalestring()
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

        self.cc_img_info        = getImageVersionFromCC(self.ccip, self.tid)
        self.nc_img_version, self.nc_img_size = getLocalImageInfo(self.srcimgid)
        self.nc_dbsize          = getLocalDatabaseInfo(self.srcimgid, self.insid)

        if paras == 'luhya':
            prompt      = locale_string['prmptDfromCC2NC_image']
            source      = "rsync://%s/%s/%s" % (self.ccip, data['rsync'], self.srcimgid)
            destination = "/storage/images/"

            if self.cc_img_info['data']['version'] == self.nc_img_version and \
               self.cc_img_info['data']['size'] == self.nc_img_size and \
               self.nc_img_size > 0:
                payload['progress'] = 0
                payload['done']     = 1
                self.forwardTaskStatus2CC(json.dumps(payload))
                logger.error("image in cc is SAME as that in nc. ")
                return retvalue
            else:
                payload['prompt'] = prompt
                imgid = self.srcimgid
                if imgid in img_tasks_status.keys():
                    if not self.tid in img_tasks_status[imgid]['tids']:
                        img_tasks_status[imgid]['tids'].apppend(self.tid)
                    worker = img_tasks_status[imgid]['worker']
                else:
                    img_tasks_status[imgid]= {}
                    img_tasks_status[imgid]['tids'] = [self.tid]
                    worker = rsyncWorkerThread(logger, source, destination)
                    worker.start()
                    img_tasks_status[imgid]['worker'] = worker

        if paras == 'db':
            prompt      = locale_string['prmptDfromCC2NC_db']
            source      = "rsync://%s/%s/%s" % (self.ccip, data['rsync'], self.srcimgid)
            destination = "/storage/space/database/images/"

            if self.cc_img_info['data']['dbsize'] == self.nc_dbsize and \
               self.nc_dbsize > 0:
                payload['progress'] = 0
                payload['done']     = 1
                self.forwardTaskStatus2CC(json.dumps(payload))
                logger.error("database in cc is SAME as that in nc. ")
                return retvalue
            else:
                payload['prompt'] = prompt
                imgid = self.srcimgid
                if imgid in db_tasks_status.keys():
                    if not self.tid in db_tasks_status[imgid]['tids']:
                        db_tasks_status[imgid]['tids'].apppend(self.tid)
                    worker = self.db_tasks_status[imgid]['worker']
                else:
                    db_tasks_status[imgid]= {}
                    db_tasks_status[imgid]['tids'] = [self.tid]
                    worker = rsyncWorkerThread(logger, source, destination)
                    worker.start()
                    db_tasks_status[imgid]['worker'] = worker


        while True:
            payload['progress'] = worker.getprogress()
            payload['failed'] = worker.isFailed()
            payload['done'] = worker.isDone()
            if worker.isFailed():
                logger.error(' ----- failed . ')
                payload['failed']   = worker.isFailed()
                payload['errormsg'] = worker.getErrorMsg()
                payload['state']    = 'init'
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

        if worker.isFailed() or worker.isDone():
            if paras == 'luhya':
                del self.img_tasks_status[imgid]
            if paras == 'db':
                del self.db_tasks_status[imgid]

        return retvalue

    def cloneImage(self, data):
        logger.error('cloneImage start ... ...')
        retvalue = "OK"
        locale_string = getlocalestring()

        payload = {
                'type'      : 'taskstatus',
                'phase'     : "preparing",
                'state'     : "cloning",
                'progress'  : 0,
                'tid'       : self.tid,
                'prompt'    : '',
                'errormsg'  : "",
                'failed'    : 0,
                'done'      : 0,
        }

        dstfile  = None
        hdds = get_vm_hdds()
        need_delete = False
        need_clone  = False

        if data['rsync'] == 'luhya':
            payload['prompt'] =  locale_string['promptClone_image']
            srcfile  = "/storage/images/%s/machine"      % self.srcimgid
            dstfile  = "/storage/tmp/images/%s/machine"  % self.dstimgid
            if self.srcimgid != self.dstimgid:
                need_clone  = True
                need_delete = True

        if data['rsync'] == 'db':
            payload['prompt'] =  locale_string['promptClone_db']
            srcfile  = "/storage/space/database/images/%s/database" % self.srcimgid
            if self.insid.find('TMP') == 0:
                dstfile  = "/storage/space/database/images/%s/database" % self.dstimgid
                if self.srcimgid != self.dstimgid:
                    need_delete = True
                    need_clone  = True
                else:
                    need_delete = False
                    need_clone  = False

            if self.insid.find('VD')  == 0 or self.insid.find('TVD') == 0 :
                pass
            if self.insid.find('VS')  == 0:
                dstfile  = "/storage/space/database/instances/%s/database" % self.insid
                if dstfile in hdds or os.path.exists(dstfile):
                    pass
                else:
                    need_clone = True

        if need_delete == True:
            cmd = VBOX_MGR_CMD + " closemedium disk %s --delete" % dstfile
            logger.error("cmd line = %s", cmd)
            commands.getoutput(cmd)

            if os.path.exists(os.path.dirname(dstfile)):
                shutil.rmtree(os.path.dirname(dstfile))

        if need_clone == True:
            src_size = os.path.getsize(srcfile)
            cmd = VBOX_MGR_CMD + " clonehd " + " " + srcfile + " " + dstfile
            logger.error("cmd line = %s", cmd)
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
        done_1 = False
        done_2 = False

        data = {}
        data['cmd']     = 'image/prepare'
        data['tid']     =  self.tid
        data['rsync']   = 'luhya'
        try:
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

            if done_1 == False or done_2 == False:
                logger.error('send cmd image/prepare/failure ')
                self.download_rpc.call(cmd="image/prepare/failure", tid=data['tid'], paras=data['rsync'])
            else:
                logger.error('send cmd image/prepare/success ')
                self.download_rpc.call(cmd="image/prepare/success", tid=data['tid'], paras=data['rsync'])
                payload = json.dumps(payload)
                self.forwardTaskStatus2CC(payload)
        except Exception as e:
            logger.error("prepareImageTask Exception: %s" % str(e))
            logger.error('send cmd image/prepare/failure ')
            self.download_rpc.call(cmd="image/prepare/failure", tid=data['tid'], paras=data['rsync'])

            payload['failed'] = 1
            payload['errormsg'] = str(e)
            payload['state'] = 'init'
            self.forwardTaskStatus2CC(json.dumps(payload))

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
            self.vm_root_dir = "/storage/tmp/"
            self.root_dir    = "/storage/tmp/images/"
        else:
            self.vm_root_dir = "/storage/"
            self.root_dir    = "/storage/images/"
        self.vboxmgr = vboxWrapper(self.dstimgid, self.insid, self.vm_root_dir)

    # RPC call to ask CC download image from walrus
    def submitFromCC2Walrus(self, data):
        logger.error('submitFromCC2Walrus start ... ...')
        retvalue = "OK"

        while True:
            response = self.download_rpc.call(cmd=data['cmd'], tid=data['tid'], paras=data['rsync'])
            response = json.loads(response)

            if response['failed'] == 1:
                logger.error(' ----- failed . ')
                response['state'] = 'init'
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
        locale_string = getlocalestring()

        payload = {
            'type'      : 'taskstatus',
            'phase'     : "submitting",
            'state'     : 'uploading',
            'progress'  : 0,
            'tid'       : self.tid,
            'prompt'    : '',
            'errormsg'  : "",
            'failed'    : 0,
            'done'      : 0,
        }

        retvalue = "OK"
        prompt = 'Uploading file from NC to CC ... ...'

        if amIcc() and self.srcimgid == self.dstimgid:
            logger.error(' ----- I am CC and it is modify op, no need to upload any more . ')
            payload['progress'] = 0
            payload['done']     = 1
            payload['prompt']   = prompt
            self.forwardTaskStatus2CC(json.dumps(payload))
            return retvalue

        paras = data['rsync']

        if paras == 'luhya':
            prompt      = locale_string['promptUfromNC2CC_image']
            source      = self.root_dir + self.dstimgid
            destination = "rsync://%s/%s/" % (self.ccip, data['rsync'])
            payload['prompt'] = prompt
        if paras == 'db':
            prompt      = locale_string['promptUfromNC2CC_db']
            payload['prompt'] = prompt
            payload['progress'] = 0
            payload['done']   = 1
            self.forwardTaskStatus2CC(json.dumps(payload))
            return retvalue

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

    def delete_snapshort(self):
        logger.error(' -------- delete_snapshort')

        snapshot_name = "thomas"
        if self.vboxmgr.isSnapshotExist(snapshot_name):
            out = self.vboxmgr.delete_snapshot(snapshot_name)
            logger.error("luhya: delete snapshort with result - out=%s ", out)

    def task_finished(self):
        logger.error(' -------- task_finished')

        find_registered_vm = False
        vminfo = getVMlist()
        for vm in vminfo:
            if vm['insid'] == self.insid:
                find_registered_vm = True
                break

        if self.srcimgid != self.dstimgid:
            if find_registered_vm == True:
                ret = self.vboxmgr.unregisterVM()
                logger.error("--- vboxmgr.unregisterVM ret=%s" % (ret))
                self.vboxmgr.deleteVMConfigFile()

            hdds = get_vm_hdds()
            dstfile = '/storage/tmp/images/%s/machine' % self.dstimgid
            if dstfile in hdds:
                cmd = VBOX_MGR_CMD + " closemedium disk %s --delete" % dstfile
                logger.error("cmd line = %s", cmd)
                commands.getoutput(cmd)

            if os.path.exists(os.path.dirname(dstfile)):
                logger.error('rm %s' % os.path.dirname(dstfile))
                if os.path.exists(os.path.dirname(dstfile)):
                    shutil.rmtree(os.path.dirname(dstfile))

            logger.error("--- task_finish is Done whit src <> dst")
        else:
            if find_registered_vm == True:
                ret = self.vboxmgr.unregisterVM()
                self.vboxmgr.deleteVMConfigFile()
                logger.error("--- vboxmgr.unregisterVM ret=%s" % (ret))

            oldversionNo = ReadImageVersionFile(self.dstimgid)
            newversionNo = IncreaseImageVersion(oldversionNo)
            WriteImageVersionFile(self.dstimgid, newversionNo)
            logger.error("update version to %s" % newversionNo)
            logger.error("--- task_finish is Done whit src == dst")

    def run(self):
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

        done_1 = False
        done_2 = False

        data = {}
        data['cmd']     = 'image/submit'
        data['tid']     =  self.tid
        data['rsync']   = 'luhya'
        try:
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

            if done_1 == False or done_2 == False:
                logger.error('send cmd image/submit/failure ')
                self.download_rpc.call(cmd="image/submit/failure", tid=data['tid'], paras=data['rsync'])
            else:
                self.task_finished()
                payload = json.dumps(payload)
                self.forwardTaskStatus2CC(payload)

                logger.error('send cmd image/submit/success whith payload=%s' % payload)
                self.download_rpc.call(cmd="image/submit/success", tid=data['tid'], paras=data['rsync'])

        except Exception as e:
            logger.error("submitImageTask Exception Error Message : %s" % str(e))
            logger.error('send cmd image/submit/failure ')
            self.download_rpc.call(cmd="image/submit/failure", tid=self.tid, paras=data['rsync'])

            payload['failed'] = 1
            payload['errormsg'] = str(e)
            payload['state'] = 'init'
            self.forwardTaskStatus2CC(json.dumps(payload))


img_tasks_status = {}
db_tasks_status  = {}

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

        if self.srcimgid != self.dstimgid:
            self.rootdir = "/storage/tmp"
        else:
            self.rootdir = "/storage"

    def vbox_createVM(self):
        self.vboxmgr = vboxWrapper(self.dstimgid, self.insid, self.rootdir)

        flag = True
        payload = {
            'type'      : 'taskstatus',
            'phase'     : "editing",
            'state'     : 'booting',
            'tid'       : self.tid,
            'errormsg'  : '',
            'failed'    : 0,
        }

        vboxmgr = self.vboxmgr
        bridged_ifs = get_vm_ifs()

        # register VM
        if not vboxmgr.isVMRegistered():
            logger.error("--- --- --- vm %s is not registered" % vboxmgr.getVMName())
            if vboxmgr.isVMRegisteredBefore():
                logger.error("--- --- --- vm %s is registered before" % vboxmgr.getVMName())
                ret = vboxmgr.registerVM()
            else:
                logger.error("--- --- --- vm %s is not registered yet" % vboxmgr.getVMName())
                try:
                    ostype_value = self.runtime_option['ostype']
                    ret = vboxmgr.createVM(ostype=ostype_value)
                    logger.error("--- --- --- vboxmgr.createVM, error=%s" % ret)
                    ret = vboxmgr.registerVM()
                    logger.error("--- --- --- vboxmgr.registerVM, error=%s" % ret)
                    if self.runtime_option['disk_type'] == 'IDE':
                        ret = vboxmgr.addCtrl(" --name IDE --add ide ")
                    else:
                        ret = vboxmgr.addCtrl(" --name SATA --add sata ")
                        ret = vboxmgr.addCtrl(" --name IDE --add ide ")
                        # ret, err = vboxmgr.addCtrl(" --name IDE --add ide ")
                    logger.error("--- --- --- vboxmgr.addCtrl, error=%s" % ret)

                    # add disks
                    for disk in self.runtime_option['disks']:
                        ret = vboxmgr.attachHDD(self.runtime_option['disk_type'], disk['mtype'], disk['file'])
                        logger.error("--- --- --- vboxmgr.attachHDD %s, error=%s" % (disk['file'], ret))
                        time.sleep(2)

                    # add folders
                    for folder in self.runtime_option['folders']:
                        ret = vboxmgr.attachSharedFolder(folder['name'], folder['path'])
                        logger.error("--- --- --- vboxmgr.attachSharedFolder %s=%s, error=%s" % (folder['name'], folder['path'] , ret))
                        time.sleep(2)

                    # in servere side, each VM has 4G mem
                    _cpus    = self.runtime_option['cpus']
                    _memory  = self.runtime_option['memory'] * 1024
                    if self.runtime_option['usage'] == 'desktop':
                        _network_para = " --nic1 nat  --nictype1 %s " % self.runtime_option['networkcards'][0]['nic_type']
                    else:
                        _network_para = " --nic1 bridged --bridgeadapter1 %s --nictype1 %s --macaddress1 %s" % (bridged_ifs[0], self.runtime_option['networkcards'][0]['nic_type'], self.runtime_option['networkcards'][0]['nic_mac'])
                    ostypepara_value = _network_para +  self.runtime_option['audio_para']
                    ret = vboxmgr.modifyVM(osTypeparam=ostypepara_value, cpus = _cpus, mem=_memory, )
                    logger.error("--- --- --- vboxmgr.modifyVM, error=%s" % ret)

                    # in server side, configure headless property
                    portNum = self.runtime_option['rdp_port']
                    ret = vboxmgr.addHeadlessProperty(port=portNum)
                    logger.error("--- --- --- vboxmgr.addHeadlessProperty, error=%s" % ret)

                    if self.runtime_option['usage'] == 'desktop':
                        ret = vboxmgr.addVRDPproperty()
                        logger.error("--- --- --- vboxmgr.addVRDPproperty for video channel, error=%s" % ret)

                    vboxmgr.unregisterVM()
                    vboxmgr.registerVM()

                except Exception as e:
                    logger.error("createVM Exception error=%s" % str(e))
                    ret = vboxmgr.unregisterVM()
                    vboxmgr.deleteVMConfigFile()
                    flag = False
                    payload['failed']   = 1
                    payload['state']    = 'stopped'
                    payload['errormsg'] = str(e)

        simple_send(logger, self.ccip, 'cc_status_queue', json.dumps(payload))
        logger.error('createvm result: %s' % json.dumps(payload))
        return flag


    def kvm_createVM(self):
        pass


    # need to consider vd & vs creation
    # c: d: e: f:
    def createvm(self):
        hyper = getHypervisor()
        if hyper == 'vbox':
            self.vbox_createVM()
        if hyper == 'kvm':
            self.kvm_createVM()

    def vbox_runVM(self):
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
                # every time before running, take a NEW snapshot
                snapshot_name = "thomas"
                if self.runtime_option['run_with_snapshot'] == 1:
                    if vboxmgr.isSnapshotExist(snapshot_name):
                        logger.error("--- --- --- vm %s is restore snapshot" % vboxmgr.getVMName())
                        ret = vboxmgr.restore_snapshot(snapshot_name)
                    else:
                        ret = vboxmgr.take_snapshot(snapshot_name)

                if isLNC():
                    headless = False
                else:
                    headless = True

                if self.runtime_option['protocol'] == 'NDP':
                    ret = vboxmgr.ndp_runVM(self.runtime_option['rdp_ip'], self.runtime_option['rdp_port'])
                else:
                    ret = vboxmgr.runVM(headless)

                logger.error("--- --- --- vboxmgr.runVM, error=%s" % ret)
            else:
                logger.error("--- --- --- vboxmgr.SendCAD b")
                vboxmgr.SendCAD()
        except Exception as e:
            logger.error("--- --- --- vboxmgr.runVM exception : %s " % str(e))
            flag = False
            payload['failed'] = 1
            payload['state'] = 'stopped'
            payload['errormsg'] = str(e)

        simple_send(logger, self.ccip, 'cc_status_queue', json.dumps(payload))
        logger.error('runvm result: %s' % json.dumps(payload))
        return flag

    def kvm_runVM(self):
        pass

    def runvm(self):
        hyper = getHypervisor()
        if hyper == 'vbox':
            self.vbox_runVM()
        if hyper == 'kvm':
            self.kvm_runVM()

    def run(self):
        try:
            done_1 = False
            done_2 = False

            if self.createvm() == True:
                done_1 = True
                if self.runvm() == True:
                    done_2 = True

            if done_1 == False or done_2 == False:
                self.rpcClient.call(cmd="image/edit/stopped", tid=self.tid, paras='')
            else:
                self.rpcClient.call(cmd="image/edit/running", tid=self.tid, paras='')

            # need to update nc's status at once
            update_nc_running_status()
        except Exception as e:
            logger.error("runImageTask Exception Error Message : %s" % str(e))

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

def nc_task_delete_handle(tid, runtime_option):
    logger.error("--- --- --- nc_image_delete_handle")

    retval   = tid.split(':')
    srcimgid = retval[0]
    dstimgid = retval[1]
    insid    = retval[2]

    # process for different type instance
    rootdir = "/storage"
    if srcimgid != dstimgid:
        rootdir = "/storage/tmp"

    vboxmgr = vboxWrapper(dstimgid, insid, rootdir)

    if vboxmgr.isVMRunning():
        nc_image_stop_handle(tid, runtime_option)

    find_registered_vm = False
    vminfo = getVMlist()
    for vm in vminfo:
        if vm['insid'] == insid:
            find_registered_vm = True
            break

    if find_registered_vm == True:
        ret = vboxmgr.unregisterVM()
        logger.error("--- vboxmgr.unregisterVM ret=%s" % (ret))
    ret = vboxmgr.deleteVMConfigFile()
    logger.error("--- vboxmgr.deleteVMConfigFile ret=%s" % (ret))


    hdds = get_vm_hdds()
    disks = []
    if insid.find('TMP') == 0:
        if srcimgid != dstimgid:
            disks.append('/storage/tmp/images/%s/machine' % dstimgid)

    if insid.find('VD') == 0 or insid.find('TVD') == 0:
        pass

    if insid.find('VS') == 0:
        pass

    for disk in disks:
        if disk in hdds:
            cmd = VBOX_MGR_CMD + " closemedium disk %s --delete" % disk
            logger.error("cmd line = %s", cmd)
            commands.getoutput(cmd)

        if os.path.exists(os.path.dirname(disk)):
            logger.error('rm %s' % os.path.dirname(disk))
            if os.path.exists(os.path.dirname(disk)):
                shutil.rmtree(os.path.dirname(disk))


def nc_image_stop_handle(tid, runtime_option):
    logger.error("--- --- --- nc_image_stop_handle")

    retval   = tid.split(':')
    srcimgid = retval[0]
    dstimgid = retval[1]
    insid    = retval[2]

    cmd = VBOX_MGR_CMD + " controlvm %s poweroff " % insid
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
    logger.error('update_nc_running_status')

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
    if insid.find('VD') == 0 or insid.find('TVD') == 0:
        # restore snapshot
        if vboxmgr.isSnapshotExist('thomas'):
            vboxmgr.restore_snapshot('thomas')
            logger.error('restore snapshot thomas for %s' % insid)

    # running vs   insid is VSxxxx,   when stopped, delete all except image file
    if insid.find('VS') == 0:
        # restore snapshot
        if vboxmgr.isSnapshotExist('thomas'):
            vboxmgr.restore_snapshot('thomas')
            logger.error('restore snapshot thomas for %s' % insid)

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
    'task/delete'       : nc_task_delete_handle,
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
