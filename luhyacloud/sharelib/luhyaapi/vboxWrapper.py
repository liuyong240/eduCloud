# coding=UTF-8

import os

class vboxWrapper():
    def __init__(self, imageID, rootdir):
        self._rootdir = rootdir
        self._baseVMfolder = os.path.join(rootdir, "VMs")
        self._baseImagefolder = os.path.join(rootdir, "images")
        self._tool = luhyaTools(imageID, rootdir)

        self._ide_port = 0
        self._ide_device = -1
        self._sata_port = -1
        self._sata_device = 0

    def increaseVersionNo(self, version_no="1.0.0"):
        major, minor, build = version_no.split('.')
        major = int(major)
        minor = int(minor)
        build = int(build)

        build += 1
        if build > 100:
            build = 0
            minor += 1
            if minor > 100:
                minor = 0
                major += 1

        return ("%d.%d.%d" % (major, minor, build))


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

    def modifyVM(self, mem=1024, vram=128, osTypeparam=" "):
        vm_name = self._tool._vmname

        memstr = " --memory " + str(mem)
        vramstr = " --vram " + str(vram)
        dstr = " --accelerate2dvideo on "
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

    def addCtrl(self):
        vm_name = self._tool._vmname
        storagectl = self.getVMStorageCtrl(self._ostype)
        self._storagectltype = storagectl.split()[1]

        firstCtl = " --name IDE --add ide "
        cmd_line = "VBoxManage storagectl " + vm_name + firstCtl
        ret, err = self._tool.runCMDline(cmd_line)

        secondCtl = " --name SATA --add sata "
        cmd_line = "VBoxManage storagectl " + vm_name + secondCtl
        ret, err = self._tool.runCMDline(cmd_line)

        return ret, err

    def portDeviceNumberAdd(self, hddtype = ""):
		if hddtype == "IDE" or self._storagectltype == "IDE":
			self._ide_device += 1
			return self._ide_port, self._ide_device
		elif hddtype == "SATA" or self._storagectltype == "SATA":
			self._sata_port += 1
			return self._sata_port, self._sata_device
		else:
			return 100, 100

    def attachHDD_c(self, storageCtl="IDE", mtype="normal", admin=False):
        vm_name = self._tool._vmname
        vmfile = self._tool._image_file

        port, device = self.portDeviceNumberAdd()
        cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', self._storagectltype, '--port', str(port), '--device',
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

    def attachHDD_shared_d(self, storageCtl="IDE", mtype="multiattach",
                           imgfile="/storage/images/diskd.vdi"):
        vm_name = self._tool._vmname
        dest_diskd = imgfile

        if self._storagectltype == "SATA":
            return " ", " "

        if os.path.exists(dest_diskd):
            port, device = self.portDeviceNumberAdd("IDE")
            cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', 'IDE', '--port', str(port), '--device',
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
            port, device = self.portDeviceNumberAdd()
            cmd_line = ['VBoxManage', 'storageattach', vm_name, '--storagectl', self._storagectltype, '--port', str(port), '--device',
                        str(device), '--type', 'dvddrive', '--medium', 'host:/dev/sr0', '--mtype', mtype, '--passthrough', 'on']
            ret, err = self._tool.runCMDline(cmd_line, False)
        return ret, err

    def attachSharedFolder(self, path=None):
        vm_name = self._tool._vmname
        if path == None:
            conf = configuration(self._tool._conf);
            sharedfolder_path = conf.getvalue("sharedfolder", "hostpath")
        else:
            sharedfolder_path = path

        cmd_line = "vboxmanage sharedfolder add " + vm_name + " --name software " + " --hostpath " + sharedfolder_path + " --automount "
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