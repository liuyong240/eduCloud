# coding=UTF-8
import os
import platform as pf
import _winreg
from _winreg import ConnectRegistry, OpenKey, CloseKey, QueryInfoKey, SetValueEx
from uuid import getnode as get_mac
import wmi

TMP = os.environ['TMP']

hostname_config = {
    "bnamechange"   : "NAMEFLAG",
    "breboot"       : "BOOTFLAG",
    "newname"       : "new-host-name",
}

hostipaddr_config = {
    "bipchange"     : "IPFLAG",
    "ipaddr"        : ["new-host-ipaddr"],
    "ipmask"        : ["new-host-ipmask"],
    "ipgateway"     : ["new-host-ipgateway"],
    "ipdns"         : ["new-host-dns"]
}

def getActiveMAC():
    mac = get_mac()
    return ':'.join(("%012X" % mac)[i:i + 2] for i in range(0, 12, 2))


def getWindowsVersion():
    ver_str = pf.uname()
    if ver_str[2] == 'xp':
        return "WinXP"
    if ver_str[2] == '7':
        return "Win7"


def setHostIP():
    if hostipaddr_config["bipchange"] != "Yes":
        return

    wmiService = wmi.WMI()
    colNicConfigs = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    if len(colNicConfigs) < 1:
        return  # no active network adaptor

    objNicConfig = colNicConfigs[0]  # get first adaptor
    returnValue = objNicConfig.EnableStatic(IPAddress=hostipaddr_config["ipaddr"],SubnetMask=hostipaddr_config["ipmask"])
    returnValue = objNicConfig.SetGateways(DefaultIPGateway=hostipaddr_config["ipgateway"], GatewayCostMetric=[1])
    returnValue = objNicConfig.SetDNSServerSearchOrder(DNSServerSearchOrder=hostipaddr_config["ipdns"])
    return returnValue


def setHostName():
    if hostname_config['bnamechange'] != "Yes":
        return

    aKey = OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\ControlSet001\Control\ComputerName\ActiveComputerName', 0,
                   _winreg.KEY_ALL_ACCESS)
    SetValueEx(aKey, "ComputerName", 0, _winreg.REG_SZ, hostname_config['newname'])
    CloseKey(aKey)

    aKey = OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Control\ComputerName\ComputerName", 0,
                   _winreg.KEY_ALL_ACCESS)
    SetValueEx(aKey, "ComputerName", 0, _winreg.REG_SZ, hostname_config['newname'])
    CloseKey(aKey)

    aKey = OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\services\Tcpip\Parameters", 0,
                   _winreg.KEY_ALL_ACCESS)
    SetValueEx(aKey, "NV Hostname", 0, _winreg.REG_SZ, hostname_config['newname'])
    CloseKey(aKey)

    aKey = OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\services\Tcpip\Parameters", 0,
                   _winreg.KEY_ALL_ACCESS)
    SetValueEx(aKey, "Hostname", 0, _winreg.REG_SZ, hostname_config['newname'])
    CloseKey(aKey)

    if hostname_config['breboot'] != "Yes":
        os.system("shutdown /r /t 0")


def changeHostName():
    hostname = '%s\\hostname.txt' % TMP
    with open(hostname, 'w') as myfile:
        myfile.write('changeHostName')


def changeHostIP():
    ipaddr = '%s\\ipaddr.txt' % TMP
    with open(ipaddr, 'w') as myfile:
        myfile.write('changeHostIP')


def changeHost():
    setHostIP()
    setHostName()

if __name__ == "__main__":
    changeHost()