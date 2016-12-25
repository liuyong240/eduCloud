# coding=UTF-8

import os
from luhyaapi.luhyaTools import *
from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *
import json
import subprocess

logger = getncdaemonlogger()

VBOX_MGR_CMD = "VBoxManage "

def get_vm_ifs():
    cmd = VBOX_MGR_CMD + " list bridgedifs | grep Name:"
    output = commands.getoutput(cmd)

    result = []
    if len(output) > 0:
        ifs = output.split()
        num_of_ifs = len(ifs)/4
        for x in range(0, num_of_ifs):
            hd = ifs[4*x+1].strip()
            result.append(hd)

    return result

def get_vm_hdds():
    cmd = VBOX_MGR_CMD + " list hdds | grep Location"
    output = commands.getoutput(cmd)

    result = []
    if len(output) > 0:
        hdds = output.split()
        num_of_hdds = len(hdds)/2
        for x in range(0, num_of_hdds):
            hd = hdds[2*x+1].strip()
            result.append(hd)

    return result

def getVMProcessStatus(vmname):
    cmd = 'ps -C VBoxHeadless -o %cpu,%mem,cmd | grep ' + vmname
    out = commands.getoutput(cmd)
    logger.error(out)
    if len(out) > 0:
        out = out.split()
        cpu = float(out[0])
        mem = float(out[1])
        return cpu, mem

    cmd = 'ps -C NDPServer -o %cpu,%mem,cmd | grep ' + vmname
    out = commands.getoutput(cmd)
    logger.error(out)
    if len(out) > 0:
        out = out.split()
        cpu = float(out[0])
        mem = float(out[1])
        return cpu, mem

    return 0, 0

def recoverVMFromCrash():
    cmd = "/usr/local/bin/recoverVMfromCrash"
    commands.getoutput(cmd)

def getVMlistbyVBOX():
    recoverVMFromCrash()

    cmd = VBOX_MGR_CMD + " list vms"
    out = commands.getoutput(cmd)

    result = []
    if len(out) > 0:
        vms = out.split()
        num_of_vms = len(vms)/2
        for x in range(0, num_of_vms):
            vm = {}
            vm['insid'] = vms[2*x].replace('"', '')
            vm['uuid'] = vms[2*x+1].replace('{', '').replace('}', '')

            if 'inaccessible' in vm['insid']:
                logger.error("Find inaccessible vm with uuid=%s" % vm['uuid'])
                # unregister this vm by uuid
                # search for insid of this vm
                # re-register this vm by insid
                vm['guest_os'] = ''
                vm['mem'] = 0
                vm['vcpu'] = 0
                vm['state'] = 'inaccessible'
                vm['phy_mem'] = 0
                vm['phy_cpu'] = 0
                result.append(vm)
            else:
                try:
                    vm_cmd = VBOX_MGR_CMD + " showvminfo %s" % vm['insid']
                    out = execute_cmd(vm_cmd, True)
                    out = out.split('\n')
                    vm['guest_os'] =  out[2].split(':')[1].strip()  # line 3
                    tmp            =  out[8].split(':')[1].strip()  # line 9
                    vm['mem']      =  int(tmp.split('MB')[0])/1024
                    vm['vcpu']     =  int(out[15].split(':')[1].strip()) # line 16
                    state          =  out[34].split(':')[1].strip()
                    if state.find('running') >= 0:
                        vm['state'] = 'Running'
                        vm['phy_cpu'], vm['phy_mem'] = getVMProcessStatus(vm['insid'])
                    else:
                        cmd = 'ps -ef | grep ndp | grep %s | grep -v grep' % vm['insid']
                        try:
                            ret = subprocess.check_output(cmd, shell=True)
                            vm['state'] = 'Running'
                            vm['phy_cpu'], vm['phy_mem'] = getVMProcessStatus(vm['insid'])
                        except Exception as e:
                            vm['state'] = 'Stopped'
                            vm['phy_mem'] = 0
                            vm['phy_cpu'] = 0
                    result.append(vm)
                except Exception as e:
                    logger.error('%s exception = %s' % (vm_cmd, str(e)))

    #logger.error("report VMs status: %s" % json.dumps(result))
    return result

def getVMlist():
    return getVMlistbyVBOX()

class vboxWrapper():
    @staticmethod
    def clonehd(src, dst):
        cmd_line = VBOX_MGR_CMD + " clonehd %s %s " % (src, dst)
        ret = commands.getoutput(cmd_line)
        return ret

    @staticmethod
    def closemedium(dst):
        cmd_line = VBOX_MGR_CMD + " closemedium disk %s --delete" % (dst)
        ret = commands.getoutput(cmd_line)
        return ret

    @staticmethod
    def controlvm(insid):
        cmd_line = VBOX_MGR_CMD + " controlvm %s poweroff" % (insid)
        ret = commands.getoutput(cmd_line)
        return ret

    def __init__(self, imageID, name, rootdir):
        self._rootdir = rootdir
        self._baseVMfolder = os.path.join(rootdir, "VMs")
        self._baseImagefolder = os.path.join(rootdir, "images")
        self._tool = luhyaTools(imageID, name, rootdir)

        self._ide_port = 0
        self._ide_device = -1
        self._sata_port = -1
        self._sata_device = 0

    def getVMName(self):
        return self._tool._vmname

    def cloneImageFile(self, src, dst):
        cmd_line = VBOX_MGR_CMD + " clonehd " + src + " " + dst
        ret = commands.getoutput(cmd_line)
        return ret

    def createImageFile(self, filename):
        pass

    def createVM(self, ostype="WindowsXP"):
        vm_name = self._tool._vmname
        self._ostype = ostype
        cmd_line = VBOX_MGR_CMD + " createvm --name " + vm_name + " --ostype " + ostype + " --basefolder " + self._baseVMfolder
        logger.error("cmd = %s" % cmd_line)
        ret = commands.getoutput(cmd_line)
        return ret

    def registerVM(self):
        vm_name = self._tool._vmname
        xmlfile = os.path.join(self._baseVMfolder, vm_name, vm_name + ".vbox")
        cmd_line = VBOX_MGR_CMD + " registervm " + xmlfile
        logger.error("cmd = %s" % cmd_line)
        ret = commands.getoutput(cmd_line)
        return ret

    def unregisterVM(self, delete=False):
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " unregistervm " + vm_name
        if delete:
            cmd_line = cmd_line + " --delete"
        logger.error("cmd = %s" % cmd_line)
        ret = commands.getoutput(cmd_line)
        logger.error('cmd = %s' % cmd_line)
        return ret


    def take_snapshot(self, snapshot_name):
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " snapshot " + vm_name + " take " + snapshot_name
        ret = commands.getoutput(cmd_line)
        return ret

    def restore_snapshot(self, snapshot_name):
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " snapshot " + vm_name + " restore " + snapshot_name
        ret = commands.getoutput(cmd_line)
        return ret

    def delete_snapshot(self, snapshot_name):
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " snapshot " + vm_name + " delete " + snapshot_name
        ret = commands.getoutput(cmd_line)
        return ret

    def showMiniToolBar(self, flag):
        vm_name = self._tool._vmname
        if flag:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/ShowMiniToolBar on"
        else:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/ShowMiniToolBar no"
        ret = commands.getoutput(cmd_line)
        return ret

    def showFullScreen(self, flag):
        vm_name = self._tool._vmname
        if flag:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/Fullscreen on"
        else:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/Fullscreen no"
        ret = commands.getoutput(cmd_line)
        return ret

    def ndp_runVM(self, hostIP, hostPort):
        vm_name = self._tool._vmname
        cmd_line = "ndpcmd add %s %s %s" % (vm_name, hostIP, str(hostPort))
        ret = commands.getoutput(cmd_line)
        logger.error("cmd = %s" % cmd_line)
        logger.error("result = %s" % ret)

        return ret

    def runVM(self, headless):
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " startvm " + vm_name
        if headless:
            cmd_line += " --type headless"
        else:
            self.showMiniToolBar(False)
            self.showFullScreen(True)

        ret = commands.getoutput(cmd_line)
        return ret

    def isVMNDPRunning(self):
        vm_name = self._tool._vmname
        cmd = 'ps -ef | grep ndp | grep %s | grep -v grep' % vm_name
        try:
            ret = subprocess.check_output(cmd, shell=True)
            logger.error("isVMNDPRunning: %s is running" % vm_name)
            return 1
        except Exception as e:
            logger.error("isVMNDPRunning: %s is NOT running" % vm_name)
            return 0

    def isVMRunning(self):
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " list runningvms"
        ret = commands.getoutput(cmd_line)

        if not vm_name in ret:
            logger.error("isVMRunning: %s is NOT running" % vm_name)
            return self.isVMNDPRunning()
        else:
            logger.error("isVMRunning: %s is running" % vm_name)
            return 1

    #turn on/off mini toolbar
    def showMiniToolBar(self, flag):
        vm_name = self._tool._vmname
        if flag:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/ShowMiniToolBar on"
        else:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/ShowMiniToolBar no"
        ret = commands.getoutput(cmd_line)
        return ret

    # full screen or not
    def showFullScreen(self, flag):
        vm_name = self._tool._vmname
        if flag:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/Fullscreen on"
        else:
            cmd_line = VBOX_MGR_CMD + " setextradata  " + vm_name + " GUI/Fullscreen no"
        ret = commands.getoutput(cmd_line)
        return ret

    def addWirelessNetworkCard(self):
        wn = self._tool.getWirelessCardName()
        if not wn:
            return

        import xml.dom.minidom as DOM
        import codecs

        vm_name = self._tool._vmname
        xmlfile = os.path.join(self._baseVMfolder, vm_name, vm_name + ".vbox")

        doc = DOM.parse(xmlfile)
        for node in doc.getElementsByTagName("Adapter"):
            if node.parentNode.tagName == "Network":
                if node.getAttribute("slot") == "0":
                    node.setAttribute("enabled", "true")
                    break

        els = doc.createElement("BridgedInterface")
        els.setAttribute("name", wn)

        node.appendChild(els)
        xmlstr = doc.toxml()
        f = codecs.open(xmlfile, 'w', 'utf-8')
        f.write(xmlstr)
        f.close()

    def addVRDPproperty(self):
        vm_name = self._tool._vmname
        video_str = ' --vrdevideochannel on '
        video_qa  = ' --vrdevideochannelquality 75 '
        multi_str = ' --vrdemulticon on '
        cmd_line = VBOX_MGR_CMD + " modifyvm " + vm_name + video_str + video_qa + multi_str
        ret = commands.getoutput(cmd_line)
        logger.error('cmd = %s' % cmd_line)
        return ret

    # in win7, run "mstsc /v:<ip:port>"
    def addHeadlessProperty(self, port=3389):
        vm_name = self._tool._vmname
        enablestr = " --vrde on "
        authstr = " --vrdeauthtype null "
        connectstr = " --vrdemulticon on "
        portstr = " --vrdeport %d " % port
        cmd_line = VBOX_MGR_CMD + " modifyvm " + vm_name + enablestr + authstr + connectstr + portstr
        ret = commands.getoutput(cmd_line)
        logger.error('cmd = %s' % cmd_line)
        return ret

    def SendCAD(self):
        cmd = 'VBoxManage controlvm %s keyboardputscancode 1d 38 53' % self._tool._vmname
        ret = commands.getoutput(cmd)
        return ret

    def modifyVM(self, osTypeparam, cpus=1, mem=1024, vram=128):
        vm_name = self._tool._vmname

        memstr = " --memory " + str(mem)
        vramstr = " --vram " + str(vram)
        if "Windows" in self._ostype:
            dstr = " --accelerate2dvideo on "
        else:
            dstr = " "
        bioslogfade = " --bioslogofadein off --bioslogofadeout off "
        bioslogimgpath = " --bioslogoimagepath " + os.path.join(self._rootdir, "bin", "res", "BiosLogo.bmp")
        bootorder = " --boot1 disk "
        usb = " --usb on --usbehci on "
        pageFusion = ' --pagefusion on '

        vmsettingstr = vm_name + memstr + vramstr + dstr + bioslogfade +bioslogimgpath + bootorder + usb + osTypeparam + pageFusion
        cmd_line = VBOX_MGR_CMD + " modifyvm " + vmsettingstr
        logger.error("modifyvm paras = %s" % vmsettingstr)

        ret = commands.getoutput(cmd_line)
        logger.error('cmd = %s' % cmd_line)
        return ret

    def getVMStorageCtrl(self, ostype):
        storagectl=""

        try:
            conf = configuration('/storage/config/vboxvm.conf')
            storagectl = conf.getvalue(ostype, 'storagectrl').strip('"')
        except:
            pass

        return storagectl

    def getVMOSTypeParam(self, ostype):
        ostypepara = ""

        try:
            conf = configuration('/storage/config/vboxvm.conf')
            ostypepara = conf.getvalue(ostype, 'vmpara').strip('"')
        except:
            pass

        return ostypepara

    def addCtrl(self, storagectl):
        vm_name = self._tool._vmname

        cmd_line = VBOX_MGR_CMD + " storagectl " + vm_name + storagectl
        logger.error("cmd = %s" % cmd_line)
        ret = commands.getoutput(cmd_line)
        return ret

    def portDeviceNumberAdd(self, hddtype):
        if hddtype == "IDE":
            self._ide_device += 1
            if self._ide_device > 1:
                self._ide_port += 1
                self._ide_device = 0

            port = self._ide_port
            device = self._ide_device
        else:
            self._sata_port += 1
            port =  self._sata_port
            device = self._sata_device
        return port, device

    def attachHDD(self, storageCtl, mtype, imgfile):
        ret = ""
        vm_name = self._tool._vmname
        if not os.path.exists(imgfile):
            err = "FileNotExist: " + imgfile
        else:
            port, device = self.portDeviceNumberAdd(storageCtl)
            cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', storageCtl, '--port', str(port), '--device', str(device), '--type', 'hdd', '--medium', imgfile, '--mtype', mtype]
            cmd_line = ' '.join(map(lambda x: '%s' % x, cmd_line))
            ret = commands.getoutput(cmd_line)
            logger.error('cmd = %s' % cmd_line)
        return ret

    # VBoxManage storageattach test  --storagectl IDE --port 1 --device 0 --type dvddrive --medium host:/dev/sr0 --mtype readonly --passthrough on
    def attachDVD(self, storageCtl="IDE", mtype="readonly"):
        ret = ""
        if not os.path.exists("/dev/sr0"):
            err = "DVD Not Exist"
        else:
            vm_name = self._tool._vmname
            port, device = self.portDeviceNumberAdd(storageCtl)
            cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', self._storagectltype, '--port', str(port), '--device', str(device), '--type', 'dvddrive', '--medium', 'host:/dev/sr0', '--mtype', mtype, '--passthrough', 'on']
            cmd_line = ' '.join(map(lambda x: '%s' % x, cmd_line))
            ret = commands.getoutput(cmd_line)
        return ret

    def attachSharedFolder(self, name, path):
        vm_name = self._tool._vmname

        cmd_line = VBOX_MGR_CMD + " sharedfolder add " + vm_name + " --name " + name  + " --hostpath " + path + " --automount "
        ret = commands.getoutput(cmd_line)
        logger.error('cmd = %s' % cmd_line)
        return ret

    def isVMRegistered(self):
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " list vms"
        ret = commands.getoutput(cmd_line)
        if vm_name in ret:
            return 1
        else:
            return 0

    def isVMRegisteredBefore(self):
        vm_name = self._tool._vmname
        xmlfile = os.path.join(self._baseVMfolder, vm_name, vm_name + ".vbox")
        flag = os.path.exists(xmlfile)
        return flag

    def deleteVMConfigFile(self):
        import shutil
        try:
            vm_name = self._tool._vmname
            xmlfile = os.path.join(self._baseVMfolder, vm_name, vm_name + ".vbox")
            logger.error("xmlfile = %s" % xmlfile)
            if os.path.exists(os.path.dirname(xmlfile)):
                shutil.rmtree(os.path.dirname(xmlfile))
                if os.path.exists(os.path.dirname(xmlfile)):
                    logger.error("------ deleteVMConfigFile %s not really delete dir." % xmlfile)
        except Exception as e:
            logger.error("deleteVMConfigFile with Exception = %s" % str(e))

    def isSnapshotExist(self, snapshot_name):
        vm_name = self._tool._vmname
        flag = 0
        cmd_line = VBOX_MGR_CMD + " showvminfo " + vm_name
        ret = commands.getoutput(cmd_line)
        if "Snapshots:" in ret:
            if snapshot_name in ret:
                flag = 1
        return flag

    def CopyfiletoVM(self, file):
        src_filepath = os.path.join(self._rootdir, "bin", file)
        dst_filepath = os.path.join("c:\\luhya", file)
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " guestcontrol cp " + vm_name + " " + src_filepath + " " + dst_filepath
        authstr = " --username " + GUEST_USERNAME + " --password " + GUEST_PASSWORD
        cmd_line = cmd_line + authstr
        ret = commands.getoutput(cmd_line)
        return ret

    def RunFileOnVM(self, file):
        exe_filepath = os.path.join("c:\\luhya", file)
        vm_name = self._tool._vmname
        cmd_line = VBOX_MGR_CMD + " guestcontrol exec " + vm_name + " " + exe_filepath
        authstr = " --username " + GUEST_USERNAME + " --password " + GUEST_PASSWORD
        cmd_line = cmd_line + authstr
        ret = commands.getoutput(cmd_line)
        return ret


def getNotRunningVMs(insids):
    logger.error("start getNotRunningVMs -------- ")
    not_running_vms = []

    vbox_cmd = VBOX_MGR_CMD + " list runningvms"
    ndp_cmd  = 'ps -ef | grep ndp | grep %s | grep -v grep'
    vbox_ret = commands.getoutput(vbox_cmd)
    for insid in insids:
        if insid in vbox_ret:
            pass
        else:
            try:
                ndp_ret = subprocess.check_output((ndp_cmd % insid), shell=True)
            except Exception as e:
                logger.error("%s is NOT running. " % insid)
                not_running_vms.append(insid)

    return not_running_vms