import socket, netifaces, psutil, shutil

import random, os, commands, time
from linux_metrics import cpu_stat
from sortedcontainers import SortedList
from IPy import IP

from luhyaapi.educloudLog import *
from luhyaapi.settings import *
logger = getclclogger()



# PUBLIC or PRIVATE
def getIPType(ipaddr):
    ip = IP(ipaddr)
    return ip.iptype()

def parseTID(tid):
    _tmp = tid.split(':')
    return _tmp[0], _tmp[1], _tmp[2]

def addUserPrvDataDir(uid):
    path = '/storage/space/prv-data/%s/disk' % uid
    if not os.path.exists(path):
        os.makedirs(path)

    path = '/storage/space/prv-data/%s/data' % uid
    if not os.path.exists(path):
        os.makedirs(path)

def delUserPrvDataDir(uid):
    path = '/storage/space/prv-data/%s' % uid
    if os.path.exists(path):
        shutil.rmtree(path)

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
    if versionStr == '0.0.0':
        return '1.0.0'

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

def getLocalImageInfo(imgid):
    path = '/storage/images/' + imgid + "/machine"

    if os.path.exists(path):
        version = ReadImageVersionFile(imgid)
        size = os.path.getsize(path)
    else:
        version = '0.0.0'
        size = 0

    return version, size

def getLocalDatabaseInfo(imgid, insid):
    if insid.find('TMP') == 0:
        path = '/storage/space/database/images/' + imgid + "/database"
    else:
        path = '/storage/space/database/instances/' + insid + "/database"

    if os.path.exists(path):
        size = os.path.getsize(path)
    else:
        size = 0

    return size

def randomMAC():
    mac = [0x08, 0x00, 0x27,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ''.join(map(lambda x: "%02x" % x, mac))

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
    list_of_nic = netifaces.interfaces()
    for nic in list_of_nic:
        if not nic.startswith('lo'):
            ipstr = 'ip' + str(index)
            macstr = 'mac' + str(index)
            addr = netifaces.ifaddresses(nic)
            if netifaces.AF_INET in addr.keys():
                hostnetinfo[ipstr]  = addr[netifaces.AF_INET][0]['addr']
            if netifaces.AF_LINK in addr.keys():
                hostnetinfo[macstr] = addr[netifaces.AF_LINK][0]['addr']
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
        newport = None
    return avail_ports, used_ports, newport

def free_rdp_port(avail_port, used_port, port):
    if port in used_port:
        used_port.remove(port)
        avail_port.append(port)
    return avail_port, used_port

def allocate_web_ip(availabe_web_ips, used_web_ips):
    if len(availabe_web_ips) > 0:
        new_web_ip = availabe_web_ips[0]
        availabe_web_ips.remove(new_web_ip)
        used_web_ips.append(new_web_ip)
    else:
        new_web_ip = ''

    return availabe_web_ips, used_web_ips, new_web_ip

def free_web_ip(availabe_web_ips, used_web_ips, web_ip):
    if web_ip in used_web_ips:
        used_web_ips.remove(web_ip)
        availabe_web_ips.append(web_ip)
    return availabe_web_ips, used_web_ips

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

def DoesServiceExist(host, port, protocol='tcp'):
    # logger.error("DoesServiceExist at port=%s --- --- ", port)
    try:
        if protocol == 'tcp':
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if protocol == 'udp':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        ret = s.connect((host, port))
        s.close()
        #logger.error("Running")
        return "Running"
    except Exception as e:
        logger.error(str(e))
        return str(e)


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
    if DAEMON_DEBUG == True:
        return "Running"
    else:
        return DoesServiceExist('127.0.0.1', 80)

def restart_web():
    cmd = "sudo service apache2 restart"
    commands.getoutput(cmd)


daemon_list = {
    "clc":      "nodedaemon-clc",
    "walrus":   "nodedaemon-walrus",
    "cc":       "nodedaemon-cc",
    "nc":       "nodedaemon-nc",
    "sc":       "nodedaemon-sc",
}

def get_ndp_status(retry_num=3):
    if not isNDPed():
        return "Closed"
    else:
        return "Running"


def get_daemon_status(dtype):
    return "Running"


def restart_ndp_server():
    cmd = 'netstat -an | grep 19001'
    out = commands.getoutput(cmd)
    ret = out.find('19001')
    if ret < 0:
        # ndpserver is NOT running
        cmd_line = "sudo service ndp-server stop"
        out = os.system(cmd_line)
        cmd_line = "sudo killall -9 ndpserver"
        out = os.system(cmd_line)
        cmd_line = "sudo service ndp-server start"
        out = os.system(cmd_line)


def restart_daemon(dtype):
    cmd = "sudo service " + daemon_list[dtype] + " restart "
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

def amIclc():
    if os.path.exists('/etc/educloud/modules/clc'):
        return True
    else:
        return False

def amIcc():
    if os.path.exists('/etc/educloud/modules/cc'):
        return True
    else:
        return False

def amInc():
    if os.path.exists('/etc/educloud/modules/nc'):
        return True
    else:
        return False

def amIwalrus():
    if os.path.exists('/etc/educloud/modules/walrus'):
        return True
    else:
        return False


def getServiceStatus(dtype):
    result = {}
    result['ssh'] = get_ssh_status()
    result['web'] = get_web_status()
    result['memcache'] = get_memcache_status()
    result['amqp'] = get_amqp_status()
    result['rsync'] = get_rsync_status()
    result['daemon'] = get_daemon_status(dtype)
    result['ndp'] = get_ndp_status()

    return result

def getHostHardware():
    result = {}

    result['cpus'] = psutil.cpu_count()*2
    result['cpu_usage'] = psutil.cpu_percent()

    result['mem']  = psutil.virtual_memory().total/(1024*1024*1024) + 1
    #result['free_mem'] = (psutil.virtual_memory().total - psutil.virtual_memory().used)/(1024*1024*1024) + 1
    result['mem_usage'] = psutil.virtual_memory().percent

    result['disk'] = psutil.disk_usage("/").total /(1024*1024*1024)
    #result['free_disk'] = psutil.disk_usage("/").free /(1024*1024*1024)
    result['disk_usage'] = psutil.disk_usage("/").percent
    return result

def isLNC():
    flag = False

    if os.path.exists('/etc/redhat-release'):
        # redhat or fedora won't be lNC never.
        return flag

    cmd = "dpkg -l  | grep educloud-native-client"
    out = commands.getoutput(cmd)
    if len(out) > 0:
        lnc = out.split()[1]
        if lnc.find("educloud-native-client"):
            flag = True

    return flag

def getHypervisor():
    if os.path.exists('/usr/bin/vboxmanage'):
        return 'vbox'
    elif os.path.exists('/usr/bin/qemu-kvm'):
        return 'kvm'
    else:
        return ''

def isNDPed():
    if os.path.exists('/usr/ndp/server/NDPServer'):
        return True
    else:
        return False

def isSpiced():
    return True
