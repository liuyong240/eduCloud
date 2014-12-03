import socket, psutil, netinfo
from luhyaTools import configuration
from settings import *
import random, os, commands
from linux_metrics import cpu_stat

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

    def reset(self):
        self.stop()
        self.start()

def WriteImageVersionFile(imgid, versionStr):
    filepath = "/storage/images/" + imgid + "/version"

    text_file = open (filepath, "w")
    text_file.writelines(versionStr)
    text_file.close()

def ReadImageVersionFile(imgid):
    filepath = "/storage/images/" + imgid + "/version"
    if os.path.exists(filepath):
        text_file = open (filepath, "r")
        versionStr = text_file.readline()
        text_file.close()
        return versionStr
    else:
        return '0.0.0'

def IncreaseImageVersion(versionStr):
    major, minor, build = versionStr.split('.')
    major = int(major)
    minor = int(minor)
    build = int(build)

    build += 1
    if build > 100:
        build = 0
        minor += 1
        if minor > 100:
            minor = 0
            major += 1

    return ("%d.%d.%d" % (major, minor, build))


def randomMAC():
	mac = [ 0x00, 0x16, 0x3e,
		random.randint(0x00, 0x7f),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]
	return ':'.join(map(lambda x: "%02x" % x, mac))

def ipRange(start_ip, end_ip):
   start = list(map(int, start_ip.split(".")))
   end = list(map(int, end_ip.split(".")))
   temp = start
   ip_range = []

   ip_range.append(start_ip)
   while temp != end:
      start[3] += 1
      for i in (3, 2, 1):
         if temp[i] == 256:
            temp[i] = 0
            temp[i-1] += 1
      ip_range.append(".".join(map(str, temp)))

   return ip_range

def getccnamebyconf():
    conf = configuration('/storage/config/cc.conf')
    ccname = conf.getvalue('server', 'ccname')
    return ccname

def getccipbyconf(mydebug=False):
    conf = configuration('/storage/config/cc.conf')
    ccip = conf.getvalue('server', 'IP')
    return ccip

def getclcipbyconf(mydebug=False):
    conf = configuration('/storage/config/clc.conf')
    clcip = conf.getvalue('server', 'IP')
    return clcip

def getHostAttr():
    name   = socket.gethostname()
    cpus   = psutil.cpu_count()
    memory = psutil.virtual_memory().total/(1024*1024*1024)
    disk   = psutil.disk_usage("/").total /(1024*1024*1024)
    return name, cpus, memory, disk

def getHostNetInfo():
    hostnetinfo = {
        'exip': '',
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

    hostnetinfo['exip'] = hostnetinfo['ip0']
    return hostnetinfo

import random
def genHexRandom():
    ret = "%8x" % random.randint(0x0, 0xFFFFFFFF)
    if ret[0] == ' ':
        ret = "%8x" % random.randint(0x0, 0xFFFFFFFF)
    return ret

# network resouce allocation method
def allocate_rdp_port(avail_ports, used_ports):
    if len(avail_ports) > 0:
        newport = avail_ports[0]
        avail_ports.remove(newport)
        used_ports.append(newport)
    else:
        newport = ''
    return avail_ports, used_ports, newport

def free_rdp_port(avail_port, used_port, port):
    used_port.remove(port)
    avail_port.append(port)
    return avail_port, used_port

def allocate_ip_macs(avail_ip_masc, used_ip_macs):
    if len(avail_ip_masc) > 0:
        newipmacs = avail_ip_masc[0]
        avail_ip_masc.remove(newipmacs)
        used_ip_macs.append(newipmacs)
    else:
        newipmacs = {
            'mac': '',
            'pubip': '',
            'prvip': ''
        }

    return avail_ip_masc, used_ip_macs, newipmacs

def free_ip_macs(avail_ip_macs, used_ip_macs, ipmacs):
    used_ip_macs.remove(ipmacs)
    avail_ip_macs.append(ipmacs)

    return avail_ip_macs, used_ip_macs


def getSysCpuUtil():
    import commands
    cmd = "mpstat | tail -1 | awk '{ print 100 - $12}'"
    cpu_usage = []
    for index in range( 0, 300):
        #cpu_usage.append(commands.getoutput(cmd))
        cpu_pcts = cpu_stat.cpu_percents(0.1)
        #return '%.2f%' % (100 - cpu_pcts['idle'])
        cpu_usage.append(100 - cpu_pcts['idle'])
        # cpu_usage.append(random.randint(0x0, 100))

    return cpu_usage

def getSysDiskUtil():
    cpu_pcts = cpu_stat.cpu_percents(5)
    return '%.2f%' % (100 - cpu_pcts['idle'])

def getSysNetworkUtil():
    cpu_pcts = cpu_stat.cpu_percents(5)
    return '%.2f%' % (100 - cpu_pcts['idle'])

def getSysMemUtil():
    cpu_pcts = cpu_stat.cpu_percents(5)
    return '%.2f%' % (100 - cpu_pcts['idle'])

###########################################################################
### Service tools
import socket, commands

def DoesServiceExist(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
    except:
        return 'Closed'

    return "Running"

def get_ssh_status():
    return DoesServiceExist('127.0.0.1', 22)

def restart_ssh():
    cmd = "sudo service ssh restart"
    commands.getoutput(cmd)

def get_memcache_status():
    return DoesServiceExist('127.0.0.1', 11211)

def restart_memcache():
    cmd = "sudo service memcached restart"
    commands.getoutput(cmd)

def get_web_status():
    return DoesServiceExist('127.0.0.1', 80)

def restart_web():
    cmd = "sudo service apache2 restart"
    commands.getoutput(cmd)

def get_daemon_status():
    cmd = "sudo service educloud_daemon restart"
    output = commands.getoutput(cmd)
    if "running" in output:
        return "Running"
    else:
        return "Closed"

def restart_daemon():
    cmd = "sudo service educloud_daemon restart"
    commands.getoutput(cmd)

def get_amqp_status():
    return DoesServiceExist('127.0.0.1', 5672)

def restart_amqp():
    cmd = "sudo service rabbitmq-server restart"
    commands.getoutput(cmd)

def get_rsync_status():
    return DoesServiceExist('127.0.0.1', 873)

def restart_rsync():
    cmd = "sudo service rsync restart"
    commands.getoutput(cmd)

def getServiceStatus():
    result = {}
    result['ssh'] = get_ssh_status()
    result['web'] = get_web_status()
    result['memcache'] = get_memcache_status()
    result['amqp'] = get_amqp_status()
    result['rsync'] = get_rsync_status()
    result['daemon'] = get_daemon_status()

    return result

def getHostHardware():
    result = {}

    result['cpus'] = psutil.cpu_count()
    result['mem']  = psutil.virtual_memory().total/(1024*1024*1024)
    result['disk'] = psutil.disk_usage("/").total /(1024*1024*1024)
    return result
