import requests, json

def getWalrusInfo(clcip):
    url = "http://%s/clc/api/1.0/getwalrusinfo" % clcip
    r = requests.get(url)
    return json.loads(r.content)

def getImageInfo(clcip, imgid):
    url = "http://%s/clc/api/1.0/getimageinfo/%s" % (clcip, imgid)
    r = requests.get(url)
    return json.loads(r.content)
