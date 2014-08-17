import socket, psutil, netinfo


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

