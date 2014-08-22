import socket, psutil, netinfo
from luhyaTools import configuration
from settings import *

def getccnamebyconf():
    conf = configuration('/storage/config/cc.conf')
    ccname = conf.getvalue('server', 'ccname')
    return ccname

def getccipbyconf(mydebug=False):
    conf = configuration('/storage/config/cc.conf')
    ccip = conf.getvalue('server', 'IP')
    if debug:
        return "%s:8000" % ccip
    else:
        return ccip

def getclcipbyconf(mydebug=False):
    conf = configuration('/storage/config/clc.conf')
    clcip = conf.getvalue('server', 'IP')
    if debug:
        return "%s:8000" % clcip
    else:
        return clcip

def getHostAttr():
    name   = socket.gethostname()
    cpus   = psutil.cpu_count()
    memory = psutil.virtual_memory().total/(1024*1024*1024)
    disk   = psutil.disk_usage("/").total /(1024*1024*1024)
    return name, cpus, memory, disk

def getHostNetInfo():
    hostnetinfo = {
        'ip0':  '',
        'ip1':  '',
        'ip2':  '',
        'ip3':  '',
        'mac0': '',
        'mac1': '',
        'mac2': '',
        'mac3': '',
    }
    index = 0

    for interface in netinfo.list_active_devs():
        if not interface.startswith('lo'):
            ipstr = 'ip' + str(index)
            macstr = 'mac' + str(index)
            hostnetinfo[ipstr]  = netinfo.get_ip(interface)
            hostnetinfo[macstr] = netinfo.get_hwaddr(interface)
            index = index + 1
    return hostnetinfo

import random
def genHexRandom():
    ret = "%8x" % random.randint(0x0, 0xFFFFFFFF)
    return ret


