import requests, json, os
from settings import *
from educloudLog import *

logger = geteducloudlogger()

def isVAPPModuelEnabled():
    return os.path.exists('/etc/educloud/modules/virtapp')

def virtapp_addAccount2AD(userid, password):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/usercreate"
    else:
        url = "http://%127.0.0.1/clvirtappc/api/1.0/usercreate"
    logger.error('virtapp_addAccount2AD:' + url)
    payload = {
        'username'   : userid,
        'password'   : password,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def virtapp_removeAccount2AD(userid):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/userdelete"
    else:
        url = "http://%127.0.0.1/clvirtappc/api/1.0/userdelete"
    logger.error('virtapp_removeAccount2AD:' + url)
    payload = {
        'username'   : userid,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def virtapp_updateAccount2AD(userid, vapp_en):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/userupdate"
    else:
        url = "http://%127.0.0.1/clvirtappc/api/1.0/userupdate"
    logger.error('virtapp_updateAccount2AD:' + url)
    payload = {
        'username'   : userid,
        'vapp_en'    : vapp_en,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def virtapp_setPassword2AD(userid, password):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/setpass"
    else:
        url = "http://%127.0.0.1/clvirtappc/api/1.0/setpass"
    logger.error('virtapp_setPassword2AD:' + url)
    payload = {
        'username'   : userid,
        'password'   : password,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)
