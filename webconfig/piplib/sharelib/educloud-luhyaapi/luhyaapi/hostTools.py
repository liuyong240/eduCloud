import socket, psutil, netinfo
from luhyaTools import configuration
from vboxWrapper import *
from settings import *
import random, os, commands
from linux_metrics import cpu_stat
from sortedcontainers import SortedList


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

def getLocalImageInfo(imgid):
    path = '/storage/images/' + imgid + "/machine"

    if os.path.exists(path):
        version = ReadImageVersionFile(imgid)
        size = os.path.getsize(path)
    else:
        version = '0.0.0'
        size = 0

    return version, size

def getLocalDatabaseInfo(imgid):
    path = '/storage/space/database/images/' + imgid + "/database"

    if os.path.exists(path):
        size = os.path.getsize(path)
    else:
        size = 0

    return size

def randomMAC():
	mac = [ 0x08, 0x00, 0x27,
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
        newport = None
    return avail_ports, used_ports, newport

def free_rdp_port(avail_port, used_port, port):
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


daemon_list = {
    "clc":      "clc_daemon",
    "walrus":   "walrus_daemon",
    "cc":       "cc_daemon",
    "nc":       "nc_daemon",
    "sc":       "clc_daemon",
}

def get_daemon_status(dtype):
    cmd = "sudo service " + daemon_list[dtype] + " status "
    output = commands.getoutput(cmd)
    if "running" in output:
        return "Running"
    else:
        return "Closed"

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

def getServiceStatus(dtype):
    result = {}
    result['ssh'] = get_ssh_status()
    result['web'] = get_web_status()
    result['memcache'] = get_memcache_status()
    result['amqp'] = get_amqp_status()
    result['rsync'] = get_rsync_status()
    result['daemon'] = get_daemon_status(dtype)

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

CC_DETAIL_TEMPLATE = '''<div class="col-lg-6">
    <div class="list-group">
        <h3>Service Data</h3>
        <p class="list-group-item">
            Web Service
            <span class="pull-right text-muted"><em>{{service_data.web}}</em></span>
            <!--<button type="button" id="restart_http">Restart</button>-->
        </p>
        <p class="list-group-item">
            Daemon Service
            <span class="pull-right text-muted"><em>{{service_data.daemon}}</em></span>
            <!--<button type="button" id="restart_daemon">Restart</button>-->
        </p>
        <p class="list-group-item">
            SSH Service
            <span class="pull-right text-muted"><em>{{service_data.ssh}}</em></span>
            <!--<button type="button" id="restart_ssh">Restart</button>-->
        </p>
        <p class="list-group-item">
            RSYNC Service
            <span class="pull-right text-muted"><em>{{service_data.rsync}}</em></span>
            <!--<button type="button" id="restart_rsync">Restart</button>-->
        </p>
        <p class="list-group-item">
            AMQP Service
            <span class="pull-right text-muted"><em>{{service_data.amqp}}</em></span>
            <!--<button type="button" id="restart_amqp">Restart</button>-->
        </p>
        <p class="list-group-item">
            Memcache Service
            <span class="pull-right text-muted"><em>{{service_data.memcache}}</em></span>
            <!--<button type="button" id="restart_memcache">Restart</button>-->
        </p>
        <h3>Hardware Parameters</h3>
        <p class="list-group-item">
            HostName
            <span class="pull-right text-muted"><em>{{host_ips.name}}</em></span>
        </p>
        <p class="list-group-item">
            Location
            <span class="pull-right text-muted"><em>{{host_ips.location}}</em></span>
        </p>
        <p></p>
        <p class="list-group-item">
            CPU Cores
            <span class="pull-right text-muted"><em>{{hardware_data.cpus}}</em></span>
        </p>
        <p class="list-group-item">
            CPU Usage
            <span class="pull-right text-muted"><em>{{hardware_data.cpu_usage}}%</em></span>
        </p>
        <p></p>
        <p class="list-group-item">
            Total Memory
            <span class="pull-right text-muted"><em>{{hardware_data.mem}}G</em></span>
        </p>
        <p class="list-group-item">
            Memory Usage
            <span class="pull-right text-muted"><em>{{hardware_data.mem_usage}}%</em></span>
        </p>
        <p></p>
        <p class="list-group-item">
            Total Disk
            <span class="pull-right text-muted"><em>{{hardware_data.disk}}G</em></span>
        </p>
        <p class="list-group-item">
            Disk Usage
            <span class="pull-right text-muted"><em>{{hardware_data.disk_usage}}%</em></span>
        </p>
        <p></p>
        <button id="ccres_modify" type="button" class="btn btn-primary">Network Resource Configure</button>
        <button id="permission" type="button" class="btn btn-primary">Edit Permission</button>

    </div>
</div>

<div class="col-lg-6">
    <div class="list-group">
        <div style="display:none" id="ip0"> {{host_ips.ip0}}</div>
        <div style="display:none" id="mac0">{{host_ips.mac0}}</div>
        <h3>IP Addresses</h3>
        <p class="list-group-item">
            External IP Address
            <span class="pull-right text-muted"><em>{{host_ips.eip}}</em></span>
            <button type="button" id="exip_edit">Edit</button>
        </p>
        <p class="list-group-item">
            IP Address 0
            <span class="pull-right text-muted"><em>{{host_ips.ip0}}</em></span>
        </p>
        <p class="list-group-item">
            IP Address 1
            <span class="pull-right text-muted"><em>{{host_ips.ip1}}</em></span>
        </p>
        <p class="list-group-item">
            IP Address 2
            <span class="pull-right text-muted"><em>{{host_ips.ip2}}</em></span>
        </p>
        <p class="list-group-item">
            IP Address 3
            <span class="pull-right text-muted"><em>{{host_ips.ip3}}</em></span>
        </p>
        <h3>MAC Addresses</h3>
        <p class="list-group-item">
            MAC Address 0
            <span class="pull-right text-muted"><em>{{host_ips.mac0}}</em></span>
        </p>
        <p class="list-group-item">
            MAC Address 1
            <span class="pull-right text-muted"><em>{{host_ips.mac1}}</em></span>
        </p>
        <p class="list-group-item">
            MAC Address 2
            <span class="pull-right text-muted"><em>{{host_ips.mac2}}</em></span>
        </p>
        <p class="list-group-item">
            MAC Address 3
            <span class="pull-right text-muted"><em>{{host_ips.mac3}}</em></span>
        </p>
        <p></p>
    </div>
</div> '''

VM_LIST_GROUP_ITEM = '''
        <p class="list-group-item">
            {{vminfo.insid}}
            <span class="pull-right text-muted"><em>Running</em></span>

            <p class="list-group-item">
            Guest OS<span class="pull-right text-muted"><em>{{vminfo.guest_os}}</em></span>
            </p>

            <p class="list-group-item">
            Memroy<span class="pull-right text-muted"><em>{{vminfo.mem}}G</em></span>
            </p>

            <p class="list-group-item">
            VCPU<span class="pull-right text-muted"><em>{{vminfo.vcpu}}</em></span>
            </p>
        </p>
'''

NC_DETAIL_TEMPLATE = '''<div class="col-lg-6">
    <div class="list-group">
        <h3>Virtual Machine Data</h3>
        {{vminfos}}
        <h3>Service Data</h3>
        <p class="list-group-item">
            Daemon Service
            <span class="pull-right text-muted"><em>{{service_data.daemon}}</em></span>
            <!--<button type="button" id="restart_daemon">Restart</button>-->
        </p>
        <p class="list-group-item">
            SSH Service
            <span class="pull-right text-muted"><em>{{service_data.ssh}}</em></span>
            <!--<button type="button" id="restart_ssh">Restart</button>-->
        </p>
        <h3>Hardware Parameters</h3>
        <p class="list-group-item">
            HostName
            <span class="pull-right text-muted"><em>{{host_ips.name}}</em></span>
        </p>
        <p class="list-group-item">
            Location
            <span class="pull-right text-muted"><em>{{host_ips.location}}</em></span>
        </p>
        <p></p>
        <p class="list-group-item">
            CPU Cores
            <span class="pull-right text-muted"><em>{{hardware_data.cpus}}</em></span>
        </p>
        <p class="list-group-item">
            CPU Usage
            <span class="pull-right text-muted"><em>{{hardware_data.cpu_usage}}%</em></span>
        </p>
        <p></p>
        <p class="list-group-item">
            Total Memory
            <span class="pull-right text-muted"><em>{{hardware_data.mem}}G</em></span>
        </p>
        <p class="list-group-item">
            Memory Usage
            <span class="pull-right text-muted"><em>{{hardware_data.mem_usage}}%</em></span>
        </p>
        <p></p>
        <p class="list-group-item">
            Total Disk
            <span class="pull-right text-muted"><em>{{hardware_data.disk}}G</em></span>
        </p>
        <p class="list-group-item">
            Disk Usage
            <span class="pull-right text-muted"><em>{{hardware_data.disk_usage}}%</em></span>
        </p>
        <p></p>
        <button id="permission" type="button" class="btn btn-primary">Edit Permission</button>
    </div>
</div>

<div class="col-lg-6">
    <div class="list-group">
        <div style="display:none" id="ip0"> {{host_ips.ip0}}</div>
        <div style="display:none" id="mac0">{{host_ips.mac0}}</div>
        <h3>IP Addresses</h3>
        <p class="list-group-item">
            External IP Address
            <span class="pull-right text-muted"><em>{{host_ips.eip}}</em></span>
            <button type="button" id="exip_edit">Edit</button>
        </p>
        <p class="list-group-item">
            IP Address 0
            <span class="pull-right text-muted"><em>{{host_ips.ip0}}</em></span>
        </p>
        <p class="list-group-item">
            IP Address 1
            <span class="pull-right text-muted"><em>{{host_ips.ip1}}</em></span>
        </p>
        <p class="list-group-item">
            IP Address 2
            <span class="pull-right text-muted"><em>{{host_ips.ip2}}</em></span>
        </p>
        <p class="list-group-item">
            IP Address 3
            <span class="pull-right text-muted"><em>{{host_ips.ip3}}</em></span>
        </p>
        <h3>MAC Addresses</h3>
        <p class="list-group-item">
            MAC Address 0
            <span class="pull-right text-muted"><em>{{host_ips.mac0}}</em></span>
        </p>
        <p class="list-group-item">
            MAC Address 1
            <span class="pull-right text-muted"><em>{{host_ips.mac1}}</em></span>
        </p>
        <p class="list-group-item">
            MAC Address 2
            <span class="pull-right text-muted"><em>{{host_ips.mac2}}</em></span>
        </p>
        <p class="list-group-item">
            MAC Address 3
            <span class="pull-right text-muted"><em>{{host_ips.mac3}}</em></span>
        </p>
        <p></p>
    </div>
</div> '''
