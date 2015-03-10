# coding=UTF-8
import os

if os.path.exists("/etc/educloud/modules/core") == True:
    DAEMON_DEBUG = False
    ALLOWED_VD_IN_VS_CC = False
else:
    DAEMON_DEBUG = True
    ALLOWED_VD_IN_VS_CC = True


VALID_NC_RES = {
    'server': {
        'cpu_usage'     : 10,
        'cpu'           : 2,
        'disk'          : 20,
        'mem'           : 2,
    },

    'desktop': {
        'cpu_usage'     : 20,
        'cpu'           : 1,
        'disk'          : 10,
        'mem'           : 2,
    }
}


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
            'promptUfromCC2Walrus_bd'   :   u'从集群控制器上传数据库文件到存储控制器 ... ...',

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
            'promptUfromCC2Walrus_bd'   :   u'Uploading database file from CC to Walrus ... ...',

            'promptClone_image'         :   u'Cloning image file ... ...',
            'promptClone_db'            :   u'Cloning databse file ... ...',
        }

    return my_local_string
