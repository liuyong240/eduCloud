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
