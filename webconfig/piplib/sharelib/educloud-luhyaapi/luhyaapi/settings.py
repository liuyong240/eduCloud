# coding=UTF-8
import os
import ConfigParser

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

if os.path.exists("/etc/educloud/modules/core") == True:
    DAEMON_DEBUG = False
else:
    DAEMON_DEBUG = True

def is_vd_allowed_in_vscc():
    conf_obj = configuration('/etc/educloud/modules/educloud.conf')
    ret = conf_obj.getvalue('common', 'ALLOWED_VD_IN_VS_CC')
    if ret == '1':
        return True
    else:
        return False

def get_server_res():
    res = {}
    conf_obj = configuration('/etc/educloud/modules/educloud.conf')
    res['cpu_usage'] = int(conf_obj.getvalue('server', 'cpu_usage'))
    res['cpu']       = int(conf_obj.getvalue('server', 'cpu'))
    res['disk']      = int(conf_obj.getvalue('server', 'disk'))
    res['mem']       = int(conf_obj.getvalue('server', 'mem'))
    return res

def get_desktop_res():
    res = {}
    conf_obj = configuration('/etc/educloud/modules/educloud.conf')
    res['cpu_usage'] = int(conf_obj.getvalue('desktop', 'cpu_usage'))
    res['cpu']       = int(conf_obj.getvalue('desktop', 'cpu'))
    res['disk']      = int(conf_obj.getvalue('desktop', 'disk'))
    res['mem']       = int(conf_obj.getvalue('desktop', 'mem'))
    res['max_pboot_vms']   = int(conf_obj.getvalue('desktop', 'max_pboot_vms'))
    res['max_pboot_delay'] = int(conf_obj.getvalue('desktop', 'max_pboot_delay'))

    return res

# NODE_DAEMON_LANG = 'en-us'
NODE_DAEMON_LANG = 'zh-CN'

def getlocalestring():

    if NODE_DAEMON_LANG == 'zh-CN':
        my_local_string = {
            'promptDfromWarlus2CC_image':   u'从存储控制器下载镜像文件到集群控制器 ... ...',
            'prmptDfromCC2NC_image'     :   u'从集群控制器下载镜像文件到工作服务器 ... ...',

            'promptDfromWarlus2CC_db'   :   u'从存储控制器下载数据库文件到集群控制器 ... ...',
            'prmptDfromCC2NC_db'        :   u'从集群控制器下载数据库文件到工作服务器 ... ...',

            'promptUfromNC2CC_image'    :   u'从工作服务器上传镜像文件到集群控制器 ... ...',
            'promptUfromCC2Walrus_image':   u'从集群控制器上传镜像文件到存储控制器 ... ...',

            'promptUfromNC2CC_db'       :   u'从工作服务器上传数据库文件到集群控制器 ... ...',
            'promptUfromCC2Walrus_db'   :   u'从集群控制器上传数据库文件到存储控制器 ... ...',

            'promptClone_image'         :   u'正在克隆镜像文件 ... ...',
            'promptClone_db'            :   u'正在克隆数据库文件 ... ...',
        }
    else:
        my_local_string = {
            'promptDfromWarlus2CC_image':   u'Downloading image file from Walrus to CC ... ...',
            'prmptDfromCC2NC_image'     :   u'Downloading image frile from CC to NC ... ...',

            'promptDfromWarlus2CC_db'   :   u'Downloading database file from Walrus to CC ... ...',
            'prmptDfromCC2NC_db'        :   u'Downloading database file from CC to NC ... ...',

            'promptUfromNC2CC_image'    :   u'Uploading image file from NC to CC ... ...',
            'promptUfromCC2Walrus_image':   u'Uploading image file from CC to Walrus ... ...',

            'promptUfromNC2CC_db'       :   u'Uploading database file from NC to CC ... ...',
            'promptUfromCC2Walrus_db'   :   u'Uploading database file from CC to Walrus ... ...',

            'promptClone_image'         :   u'Cloning image file ... ...',
            'promptClone_db'            :   u'Cloning databse file ... ...',
        }

    return my_local_string
