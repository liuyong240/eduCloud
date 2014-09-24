import requests, json
from settings import *

def getWalrusInfo(clcip):
    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/api/1.0/getwalrusinfo" % clcip
    else:
        url = "http://%s/clc/api/1.0/getwalrusinfo" % clcip
    r = requests.get(url)
    return json.loads(r.content)

def getImageInfo(clcip, imgid):
    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/api/1.0/getimageinfo/%s" % (clcip, imgid)
    else:
        url = "http://%s/clc/api/1.0/getimageinfo/%s" % (clcip, imgid)
    r = requests.get(url)
    return json.loads(r.content)

def getImageVersionFromCC(ccip, imgid):
    if DAEMON_DEBUG == True:
        url = "http://%s:8000/cc/api/1.0/getimageversion/%s" % (ccip, imgid)
    else:
        url = "http://%s/cc/api/1.0/getimageversion/%s" % (ccip, imgid)
    r = requests.get(url)
    return json.loads(r.content)

def submitImageFinished(clcip, tid):
    retval = tid.split(':')
    srcid = retval[0]
    dstid = retval[1]
    insid = retval[2]

    if DAEMON_DEBUG == True:
        url = "http://%s:8000/clc/image/create/task/done/%s/%s/%s" % (clcip, srcid, dstid, insid)
    else:
        url = "http://%s/clc/image/create/task/done/%s/%s/%s" % (clcip, srcid, dstid, insid)
    r = requests.get(url)
    return json.loads(r.content)

