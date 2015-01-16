# coding=UTF-8

import os, socket, commands, string, sys
from threading import *
import ConfigParser

GUEST_USERNAME = "Administrator"
GUEST_PASSWORD = "luhya"
SNAPSHOT_NAME = "luhya-thomas"

def execute_cmd(cmd_line, needsplit=True):
    out = commands.getoutput(cmd_line)
    return out

class configuration():
    def __init__(self, conf):
        self.cf = None
        self.filename = conf

        if os.path.exists(self.filename):
            self.cf = ConfigParser.ConfigParser()
            self.cf.read(self.filename)

    def getvalue(self, section, name):
        if self.cf:
            return self.cf.get(section, name)
        else:
            return None

    def setvalue(self, section, name, value):
        if self.cf:
            return self.cf.set(section, name, value)
        else:
            return None


class vmattributes():
    def __init__(self, vmattrfile):
        self.cf = None
        self.filename = vmattrfile
        if os.path.exists(self.filename):
            self.cf = ConfigParser.ConfigParser()
            self.cf.read(self.filename)

    def getvalue(self, section, name):
        if self.cf != None:
            return self.cf.get(section, name)
        else:
            return 0

    def setvalue(self, section, name, value):
        if self.cf != None:
            self.cf.set(section, name, value)
            self.cf.write(open(self.filename, "w"))
        else:
            return None

class luhyaTools():
    def __init__(self, imageID, name, rootdir):
        self._vmname = name

        self._image_file = os.path.join(rootdir, "images", imageID, "machine")

    ########################################################
    # get VM property
    def getVMOSType(self):
        conf = configuration(self.vm_conf)
        return conf.getvalue("guest", "osType")

    def getVMMem(self):
        conf = configuration(self.vm_conf)
        return int(conf.getvalue("guest", "memory"))

    def isAutoUnregister(self):
        conf = configuration(self.vm_conf)
        return int(conf.getvalue("guest", "auto_unregister"))

    def isShowFullScreen(self):
        conf = configuration(self.vm_conf)
        return int(conf.getvalue("guest", "fullscreen"))

    def isShowMiniToolBar(self):
        conf = configuration(self.vm_conf)
        return int(conf.getvalue("guest", "minitoolbar"))

    def getNetworkType(self):
        conf = configuration(self.vm_conf)
        return conf.getvalue("guest", "network_type")

    ########################################################
    # get host property
    def isAutoUpdateVMAttr(self):
        conf = configuration(self.host_conf)
        return int(conf.getvalue("host", "auto_guest_attr_update"))

    def isOfflineEnabled(self):
        conf = configuration(self.host_conf)
        return int(conf.getvalue("host", "offline_enabled"))

    def isAutoPowerOffHost(self):
        conf = configuration(self.host_conf)
        return int(conf.getvalue("host", "auto_poweroff"))

    def isAutoSync(self):
        conf = configuration(self.host_conf)
        return int(conf.getvalue("host", "auto_sync"))

    def isPad(self):
        conf = configuration(self.host_conf)
        return int(conf.getvalue("host", "is_pad"))

    def increateVersion(self, ):
        vmclass = vmattributes(self._image_attr_file)
        build = int(vmclass.getvalue("Version", "build"))
        minor = int(vmclass.getvalue("Version", "minor"))
        major = int(vmclass.getvalue("Version", "major"))

        build += 1
        if build > 100:
            build = 0
            minor += 1
            if minor > 100:
                minor = 0
                major += 1

        vmclass.setvalue("Version", "build", str(build))
        vmclass.setvalue("Version", "minor", str(minor))
        vmclass.setvalue("Version", "major", str(major))

    def getRemoteVMAttrs(self, sIP, imageID):
        if self.isOfflineEnabled():
            return self.getLocalVMAttrs()
        else:
            import httplib
            import json

            conn = httplib.HTTPConnection(sIP)
            conn.request('get', '/index.php?q=getvmattr')
            result = conn.getresponse().read()
            vmattrs = json.loads(result)
            conn.close()
            return vmattrs

    def getImageVersion(self, ):
        vmclass = vmattributes(self._image_attr_file)
        major = vmclass.getvalue("Version", "major")
        minor = vmclass.getvalue("Version", "minor")
        build = vmclass.getvalue("Version", "build")
        return int(major), int(minor), int(build)

    def PareseConfig(self, section, attr):
        ret = None
        if os.path.exists(self._conf):
            cf = ConfigParser.ConfigParser()
            cf.read(self._conf)
            ret = cf.get(section, attr)

        return ret

    def isWirelessReady(self):
        return 1

    def isServerReady(self, sever_ip):
        flag = 0
        try:
            sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sk.settimeout(1)
            sk.connect((sever_ip, 80))
            sk.close()
            flag = 1
        except Exception:
            print
            flag = 0

        return flag

    def PoweroffMachine(self, ):
        os.popen("sudo shutdown -h now")
        # os.popen("shutdown -s -t 0")


    def checkProcessExist(self, processname):
        cmd_line = "ps -ef"
        ret = commands.getoutput(cmd_line)
        if processname in ret:
            return 1
        else:
            return 0

    def getWirelessCardName(self):
        return "wlan0"

