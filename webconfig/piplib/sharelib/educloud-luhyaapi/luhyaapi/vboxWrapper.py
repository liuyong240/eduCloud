# coding=UTF-8

import os
from luhyaTools import *


def getVMlist():
    cmd = "VBoxManage list runningvms"
    out, err = execute_cmd(cmd, True)

    result = []
    if len(out) > 0:
        vms = out.split()
        num_of_vms = len(vms)/2
        for x in range(0, num_of_vms):
            vm = {}
            vm['insid'] = vms[2*x].replace('"', '')
            vm['uuid'] = vms[2*x+1].replace('{', '').replace('}', '')

            vm_cmd = "vboxmanage showvminfo %s" % vm['insid']
            out, err = execute_cmd(vm_cmd, True)
            out = out.split('\n')
            vm['guest_os'] =  out[2].split(':')[1].strip()  # line 3
            tmp            =  out[8].split(':')[1].strip()  # line 9
            vm['mem']      =  int(tmp.split('MB')[0])/1024
            vm['vcpu']     =  int(out[15].split(':')[1].strip()) # line 16

            result.append(vm)

    return result

class vboxWrapper():
    def __init__(self, imageID, name, rootdir):
        self._rootdir = rootdir
        self._baseVMfolder = os.path.join(rootdir, "VMs")
        self._baseImagefolder = os.path.join(rootdir, "images")
        self._tool = luhyaTools(imageID, name, rootdir)

        self._ide_port = 0
        self._ide_device = -1
        self._sata_port = -1
        self._sata_device = 0

    def cloneImageFile(self, src, dst):
        cmd_line = "VBoxManage clonehd " + src + " " + dst
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    def createImageFile(self, filename):
        pass


    def createVM(self, ostype="WindowsXP"):
        vm_name = self._tool._vmname
        self._ostype = ostype
        cmd_line = "VBoxManage createvm --name " + vm_name + " --ostype " + ostype + " --basefolder " + self._baseVMfolder
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    def registerVM(self):
        vm_name = self._tool._vmname
        xmlfile = os.path.join(self._baseVMfolder, vm_name, vm_name + ".vbox")
        cmd_line = "VBoxManage registervm " + xmlfile
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err


    def unregisterVM(self, delete=False):
        vm_name = self._tool._vmname
        cmd_line = "VBoxManage unregistervm " + vm_name
        if delete:
            cmd_line = cmd_line + " --delete"
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err


    def take_snapshot(self, snapshot_name):
        vm_name = self._tool._vmname
        cmd_line = "VBoxManage snapshot " + vm_name + " take " + snapshot_name
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    def restore_snapshot(self, snapshot_name):
        vm_name = self._tool._vmname
        cmd_line = "VBoxManage snapshot " + vm_name + " restore " + snapshot_name
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    def delete_snapshot(self, snapshot_name):
        vm_name = self._tool._vmname
        cmd_line = "VBoxManage snapshot " + vm_name + " delete " + snapshot_name
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err


    def runVM(self, headless=False):
        vm_name = self._tool._vmname
        cmd_line = "VBoxManage startvm " + vm_name
        if headless:
            cmd_line += " --type headless"
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    def isVMRunning(self):
        vm_name = self._tool._vmname
        cmd_line = "VBoxManage list runningvms"
        ret, err = self._tool.runCMDline(cmd_line)
        if not vm_name in ret:
            return 0
        else:
            return 1

    #turn on/off mini toolbar
    def showMiniToolBar(self, flag):
        vm_name = self._tool._vmname
        if flag:
            cmd_line = "VBoxManage setextradata  " + vm_name + " GUI/ShowMiniToolBar on"
        else:
            cmd_line = "VBoxManage setextradata  " + vm_name + " GUI/ShowMiniToolBar no"
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    # full screen or not
    def showFullScreen(self, flag):
        vm_name = self._tool._vmname
        if flag:
            cmd_line = "VBoxManage setextradata  " + vm_name + " GUI/Fullscreen on"
        else:
            cmd_line = "VBoxManage setextradata  " + vm_name + " GUI/Fullscreen no"
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

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

    # in win7, run "mstsc /v:<ip:port>"
    def addHeadlessProperty(self, port=3389):
        vm_name = self._tool._vmname
        enablestr = " --vrde on "
        authstr = " --vrdeauthtype null "
        connectstr = " --vrdemulticon on "
        portstr = " --vrdeport %d " % port
        cmd_line = "VBoxManage modifyvm " + vm_name + enablestr + authstr + connectstr + portstr
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

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

        vmsettingstr = vm_name + memstr + vramstr + dstr + bioslogfade +bioslogimgpath + bootorder + usb + osTypeparam
        cmd_line = "VBoxManage modifyvm " + vmsettingstr
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

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

        cmd_line = "VBoxManage storagectl " + vm_name + storagectl
        ret, err = self._tool.runCMDline(cmd_line)

        return ret, err

    def portDeviceNumberAdd(self, hddtype):
        port = 0
        device = 0
        if hddtype == "IDE":
            self._ide_device += 1
            port = self._ide_port
            device = self._ide_device
        else:
            self._sata_port += 1
            port =  self._sata_port
            device = self._sata_device
        return port, device

    def attachHDD_c(self, storageCtl="IDE", mtype="normal"):
        vm_name = self._tool._vmname
        vmfile = self._tool._image_file

        port, device = self.portDeviceNumberAdd(storageCtl)
        cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', storageCtl, '--port', str(port), '--device',
                    str(device), '--type', 'hdd', '--medium', vmfile, '--mtype', mtype]
        ret, err = self._tool.runCMDline(cmd_line, False)
        return ret, err

    def attachHDD_d(self, storageCtl="IDE", mtype="writethrough"):
        vm_name = self._tool._vmname

        # clone diskd for imageID
        origin_diskd = os.path.join(self._rootdir, "images", "diskd.vdi")
        dest_diskd = os.path.join(self._rootdir, "images", vm_name, vm_name+"_d.vdi")
        if not os.path.exists(dest_diskd):
            cmd_line = ["vboxmanage", "clonehd", origin_diskd, dest_diskd]
            ret, err = self._tool.runCMDline(cmd_line, False)

        port, device = self.portDeviceNumberAdd()
        cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', self._storagectltype, '--port', str(port), '--device',
                    str(device), '--type', 'hdd', '--medium', dest_diskd, '--mtype', mtype]
        ret, err = self._tool.runCMDline(cmd_line, False)
        return ret, err

    def attachHDD_shared_d(self, storageCtl="IDE", mtype="multiattach",  imgfile="/storage/images/diskd.vdi"):
        vm_name = self._tool._vmname
        dest_diskd = imgfile

        if os.path.exists(dest_diskd):
            port, device = self.portDeviceNumberAdd(storageCtl)
            cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', storageCtl, '--port', str(port), '--device',
                        str(device), '--type', 'hdd', '--medium', dest_diskd, '--mtype', mtype]
            ret, err = self._tool.runCMDline(cmd_line, False)
        else:
            err = "FileNotExist: /storage/images/diskd.vdi"
        return ret, err

    # vboxmanage storageattach test  --storagectl IDE --port 1 --device 0 --type dvddrive --medium host:/dev/sr0 --mtype readonly --passthrough on
    def attachDVD(self, storageCtl="IDE", mtype="readonly"):
        ret = ""
        err = ""
        if os.path.exists("/dev/sr0"):
            vm_name = self._tool._vmname
            port, device = self.portDeviceNumberAdd(storageCtl)
            cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', self._storagectltype, '--port', str(port), '--device',
                        str(device), '--type', 'dvddrive', '--medium', 'host:/dev/sr0', '--mtype', mtype, '--passthrough', 'on']
            ret, err = self._tool.runCMDline(cmd_line, False)
        return ret, err

    def attachSharedFolder(self, path):
        vm_name = self._tool._vmname

        cmd_line = "vboxmanage sharedfolder add " + vm_name + " --name software " + " --hostpath " + path + " --automount "
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    def isVMRegistered(self):
        vm_name = self._tool._vmname
        cmd_line = "VBoxManage list vms"
        ret, err = self._tool.runCMDline(cmd_line)
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
        vm_name = self._tool._vmname
        xmlfile = os.path.join(self._baseVMfolder, vm_name, vm_name + ".vbox")
        if os.path.exists(os.path.dirname(xmlfile)):
            shutil.rmtree(os.path.dirname(xmlfile))

    def isSnapshotExist(self, snapshot_name):
        vm_name = self._tool._vmname
        flag = 0
        cmd_line = "vboxmanage showvminfo " + vm_name
        ret, err = self._tool.runCMDline(cmd_line)
        if "Snapshots:" in ret:
            if snapshot_name in ret:
                flag = 1
        return flag

    def CopyfiletoVM(self, file):
        src_filepath = os.path.join(self._rootdir, "bin", file)
        dst_filepath = os.path.join("c:\\luhya", file)
        vm_name = self._tool._vmname
        cmd_line = "vboxmanage guestcontrol cp " + vm_name + " " + src_filepath + " " + dst_filepath
        authstr = " --username " + GUEST_USERNAME + " --password " + GUEST_PASSWORD
        cmd_line = cmd_line + authstr
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err

    def RunFileOnVM(self, file):
        exe_filepath = os.path.join("c:\\luhya", file)
        vm_name = self._tool._vmname
        cmd_line = "vboxmanage guestcontrol exec " + vm_name + " " + exe_filepath
        authstr = " --username " + GUEST_USERNAME + " --password " + GUEST_PASSWORD
        cmd_line = cmd_line + authstr
        ret, err = self._tool.runCMDline(cmd_line)
        return ret, err