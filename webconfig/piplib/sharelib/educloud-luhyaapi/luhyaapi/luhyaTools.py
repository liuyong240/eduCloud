# coding=UTF-8

import os, socket, commands, string, sys, json
from threading import *

from luhyaapi.hostTools import *
from luhyaapi.zmqWrapper import *
from luhyaapi.educloudLog import *
from luhyaapi.settings import *

logger = geteducloudlogger()

GUEST_USERNAME = "Administrator"
GUEST_PASSWORD = "luhya"
SNAPSHOT_NAME = "thomas"

# check existence of data disk,
# othervwise clone it
# ready: img file is ready
# prepare: img file is cloning
# none: img file is not exist
def makeDataDiskReady(tid, uid):
    logger.error("enter makeDataDiskReady ... ...")
    imgid, dstid, insid = parseTID(tid)

    origin_disk = '/storage/images/%s/data' % imgid
    logger.error("origin_disk = %s" % origin_disk)
    cloned_disk = '/storage/space/prv-data/%s/disk/%s/data' % (uid, imgid)
    logger.error("cloned_disk = %s" % cloned_disk)
    if os.path.exists(cloned_disk):
        origin_size = os.path.getsize(origin_disk)
        cloned_size = os.path.getsize(cloned_disk)
        if origin_size <= cloned_size:
            flag = "ready"
            per = 100
        else:
            flag = "prepare"
            per = (cloned_size * 100 / origin_size)

    else:
        flag = "none"
        per = 0.0

    if flag == "none":
        message = {}
        message['type'] = "cmd"
        message['op'] = 'clonehd/ddisk'
        message['tid'] = tid
        message['uid'] = uid

        _message = json.dumps(message)
        zmq_send('127.0.0.1', _message, CLC_CMD_QUEUE_PORT)
        logger.error("--- --- ---zmq: send clonehd/ddisk cmd to clc sucessfully")

    logger.error("makeDataDiskReady tid= %s flag = %s" % (tid,flag))
    return flag, per


# check existence of system disk,
# otherwise clone it
# assuming insid = PVDxxx
def makeSystemDiskReady(tid, uid):
    logger.error("enter makeSystemDiskReady ... ...")
    flag = 'none'
    imgid, dstid, insid = parseTID(tid)
    origin_disk = '/storage/images/%s/machine' % imgid
    cloned_disk = '/storage/pimages/%s/%s/machine' % (uid, imgid)
    # create persistent C disk for PVD
    if os.path.exists(cloned_disk):
        origin_size = os.path.getsize(origin_disk)
        cloned_size = os.path.getsize(cloned_disk)
        if origin_size <= cloned_size:
            flag = "ready"
            per = 100
        else:
            flag = "prepare"
            per = (cloned_size * 100 / origin_size)
    else:
        flag = "none"
        per = 0

    if flag == 'none':
        message = {}
        message['type'] = "cmd"
        message['op'] = 'clonehd/pvd'
        message['tid'] = tid
        message['uid'] = uid

        _message = json.dumps(message)
        zmq_send('127.0.0.1', _message, CLC_CMD_QUEUE_PORT)
        logger.error("--- --- ---zmq: send clonehd/pvd cmd to clc sucessfully")

    logger.error("makeSystemDiskReady tid= %s flag = %s" % (tid, flag))
    return flag, per

def isImageWithDDisk(imgid):
    ddisk_file = '/storage/images/%s/data' % imgid
    return os.path.exists(ddisk_file)

def execute_cmd(cmd_line, needsplit=True):
    out = commands.getoutput(cmd_line)
    return out






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

