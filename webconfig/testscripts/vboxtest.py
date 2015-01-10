from luhyaapi.vboxWrapper import *
import  json, time, shutil, os


class runImageTaskThread():
    def __init__(self, tid, runtime_option):
        retval = tid.split(':')
        self.tid      = tid
        self.srcimgid = retval[0]
        self.dstimgid = retval[1]
        self.insid    = retval[2]
        self.runtime_option = json.loads(runtime_option)
        self.idelist = ['WindowsXP', 'Windows2003', 'Windows2003_64']

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
                    if ostype_value in self.idelist:
                        ret, err = vboxmgr.addCtrl(" --name IDE --add ide ")
                    else:
                        ret, err = vboxmgr.addCtrl(" --name SATA --add sata ")
                        ret, err = vboxmgr.addCtrl(" --name IDE --add ide ")

                    ret, err = vboxmgr.attachHDD_c(storageCtl = self.runtime_option['storagectltype'])

                    snapshot_name = "thomas"
                    if not vboxmgr.isSnapshotExist(snapshot_name):
                        ret, err = vboxmgr.take_snapshot(snapshot_name)
                        
                    if self.runtime_option['usage'] == "desktop":
                        # if "Windows" in ostype_value:
                            ret, err = vboxmgr.attachHDD_shared_d(storageCtl = self.runtime_option['storagectltype'])
                        
                    # in server side, the SharedFolder is by default
                    ret, err = vboxmgr.attachSharedFolder(path="/storage/data")
                    
                    # in servere side, each VM has 4G mem
                    ostypepara_value = self.runtime_option['network']  +  self.runtime_option['waishe_para']
                    _cpus = self.runtime_option['cpus']
                    _memory  = self.runtime_option['memory']
                    ret, err = vboxmgr.modifyVM(osTypeparam=ostypepara_value, cpus = _cpus, mem=_memory, )

                    # in server side, configure headless property
                    portNum = 3301 # getUnusedPort(dID)
                    ret, err = vboxmgr.addHeadlessProperty(port=portNum)
                except:
                    ret, err = vboxmgr.unregisterVM()
                    vboxmgr.deleteVMConfigFile()
                    return

                ret, err = vboxmgr.unregisterVM()
                ret, err = vboxmgr.registerVM()
        


runtime_option = {}

# audio for MAC OS is coreaudio
# audio for Ubuntu is pulse

# for xp
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 2048
runtime_option['cpus']    = 1
runtime_option['ostype']  = "WindowsXP"
runtime_option['network'] = " --nic1 nat  --nictype1 Am79C973 "
runtime_option['storagectltype'] =  "IDE"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller ac97 "
obj = runImageTaskThread("imgtest:xp:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# for win7
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 2048
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Windows7"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82540EM "
runtime_option['storagectltype'] =  "SATA"
runtime_option['waishe_para'] = "--audio pulse --audiocontroller hda"
obj = runImageTaskThread("imgtest:win7:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# for ubuntu
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 2048
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Ubuntu_64"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82540EM "
runtime_option['storagectltype'] =  "SATA"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller ac97  "
obj = runImageTaskThread("imgtest:ubuntu:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# for win8
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 4096
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Windows8"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82540EM "
runtime_option['storagectltype'] =  "SATA"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller hda "
obj = runImageTaskThread("imgtest:win8:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# for win2003
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 4096
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Windows2003"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82545EM "
runtime_option['storagectltype'] =  "IDE"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller ac97 "
obj = runImageTaskThread("imgtest:win2003:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# for win2003_64
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 4096
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Windows2003_64"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82545EM "
runtime_option['storagectltype'] =  "IDE"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller ac97 "
obj = runImageTaskThread("imgtest:win2003_64:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# # for win2008
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 4096
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Windows2008"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82545EM "
runtime_option['storagectltype'] =  "SATA"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller hda "
obj = runImageTaskThread("imgtest:win2008:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# # for win2008_64
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 4096
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Windows2008_64"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82545EM "
runtime_option['storagectltype'] =  "SATA"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller hda "
obj = runImageTaskThread("imgtest:win2008_64:TMPINS1234", json.dumps(runtime_option))
obj.createvm()

# # for win2012_64
runtime_option['usage']   = "desktop"
runtime_option['memory']  = 4096
runtime_option['cpus']    = 1
runtime_option['ostype']  = "Windows2012_64"
runtime_option['network'] = " --nic1 bridged --bridgeadapter1 eth0 --nictype1 82545EM "
runtime_option['storagectltype'] =  "SATA"
runtime_option['waishe_para'] = " --audio pulse --audiocontroller hda "
obj = runImageTaskThread("imgtest:win2012_64:TMPINS1234", json.dumps(runtime_option))
obj.createvm()



