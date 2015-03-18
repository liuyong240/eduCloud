import requests, json
from settings import *
from educloudLog import *

logger = geteducloudlogger()

def getWalrusInfo(clcip):
    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/api/1.0/getwalrusinfo" % clcip
    else:
        url = "http://%s/clc/api/1.0/getwalrusinfo" % clcip
    logger.error('getWalrusInfo:' + url)
    r = requests.get(url)
    logger.error(r.content)
    return json.loads(r.content)

def getImageInfo(clcip, tid):
    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/api/1.0/getimageinfo" % (clcip)
    else:
        url = "http://%s/clc/api/1.0/getimageinfo" % (clcip)
    logger.error('getImageInfo:' + url)
    payload = {
        'tid'   : tid
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def getImageVersionFromCC(ccip, tid):
    if DAEMON_DEBUG == True:
        url = "http://%s:8000/cc/api/1.0/getimageversion" % (ccip)
    else:
        url = "http://%s/cc/api/1.0/getimageversion" % (ccip)
    logger.error('getImageVersionFromCC:' + url)
    payload = {
        'tid' : tid
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def verify_clc_cc_image_info(ccip, tid):
    if DAEMON_DEBUG == True:
        url = "http://%s:8000/cc/api/1.0/verify/clc/cc/file/ver" % (ccip)
    else:
        url = "http://%s/cc/api/1.0/verify/clc/cc/file/ver" % (ccip)
    logger.error('verify_clc_cc_image_info:' + url)
    payload = {
        'tid'   : tid,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def prepareImageFailed(clcip, tid):
    retval = tid.split(':')
    srcid = retval[0]
    dstid = retval[1]
    insid = retval[2]

    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/image/create/task/prepare/failure/%s/%s/%s" % (clcip, srcid, dstid, insid)
    else:
        url = "http://%s/clc/image/create/task/prepare/failure/%s/%s/%s" % (clcip, srcid, dstid, insid)
    logger.error('prepareImageFailed:' + url)
    r = requests.get(url)
    logger.error(r.content)
    return json.loads(r.content)

def prepareImageFinished(clcip, tid):
    retval = tid.split(':')
    srcid = retval[0]
    dstid = retval[1]
    insid = retval[2]

    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/image/create/task/prepare/success/%s/%s/%s" % (clcip, srcid, dstid, insid)
    else:
        url = "http://%s/clc/image/create/task/prepare/success/%s/%s/%s" % (clcip, srcid, dstid, insid)
    logger.error('prepareImageFinished:' + url)
    r = requests.get(url)
    logger.error(r.content)
    return json.loads(r.content)

def submitImageFailed(clcip, tid):
    retval = tid.split(':')
    srcid = retval[0]
    dstid = retval[1]
    insid = retval[2]

    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/image/create/task/submit/failure/%s/%s/%s" % (clcip, srcid, dstid, insid)
    else:
        url = "http://%s/clc/image/create/task/submit/failure/%s/%s/%s" % (clcip, srcid, dstid, insid)
    logger.error('submitImageFailed:' + url)
    r = requests.get(url)
    logger.error(r.content)
    return json.loads(r.content)

def submitImageFinished(clcip, tid):
    retval = tid.split(':')
    srcid = retval[0]
    dstid = retval[1]
    insid = retval[2]

    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/image/create/task/submit/success/%s/%s/%s" % (clcip, srcid, dstid, insid)
    else:
        url = "http://%s/clc/image/create/task/submit/success/%s/%s/%s" % (clcip, srcid, dstid, insid)
    logger.error('submitImageFinished:' + url)
    r = requests.get(url)
    logger.error(r.content)
    return json.loads(r.content)

def updateVMStatus(clcip, tid, status):
    retval = tid.split(':')
    srcid = retval[0]
    dstid = retval[1]
    insid = retval[2]

    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/image/create/task/updatevmstatus/%s/%s/%s/%s" % (clcip, srcid, dstid, insid, status)
    else:
        url = "http://%s/clc/image/create/task/updatevmstatus/%s/%s/%s/%s" % (clcip, srcid, dstid, insid, status)
    logger.error('updateVMStatus:' + url)
    r = requests.get(url)
    logger.error(r.content)
    return json.loads(r.content)

