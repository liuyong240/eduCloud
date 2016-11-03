import os, sys, time, commands
from client_sdk import *

sep = os.sep
if sep == '/': # it is Linux
    RDP_CLIENT_EXECUTE_PATH = 'rdesktop %s'
else:
    RDP_CLIENT_EXECUTE_PATH = 'mstsc /f zv:%s'


vmw = cloudDesktopWrapper()
vmw.setHost('192.168.56.104', 80)
vmw.setUser('test', 'test')

if not vmw.logon():
    print 'logon failed, try correct user name & password'
    sys.exit(-1)

# get list of vms
list_vms = vmw.getVDList()
vmobj = list_vms['data'][0]

if vmobj['phase'] == 'editing':
    if vmobj['state'] == 'running' or vmobj['state'] == 'Running':
        ret = vmw.getRDPUrl(vmobj)
        if ret['Result'] == 'FAIL':
            print ret['error']
            sys.exit(-1)

        rdp_client_cmd = RDP_CLIENT_EXECUTE_PATH %  ret['mgr_url']
        commands.getoutput(rdp_client_cmd)
        sys.exit(0)

ret = vmw.startVM(vmobj)
if ret['Result'] == 'FAIL':
    print ret['error']
    vmw.errorHandle(vmobj)
    sys.exit(-1)
else:
    vmobj['tid'] = ret['tid']

ret = vmw.prepareVM(vmobj)
if ret['Result'] == 'FAIL':
    print ret['error']
    vmw.errorHandle(vmobj)
    sys.exit(-1)

while (1):
    time.sleep(2)
    ret = vmw.getPrepareProgress(vmobj)
    print 'download progress = %s' % ret['progress']
    if ret['phase'] == 'preparing' and ret['state'] == 'done':
        break

ret = vmw.runVM(vmobj)
if ret['Result'] == 'FAIL':
    print ret['error']
    vmw.errorHandle(vmobj)
    sys.exit(-1)

while (1):
    time.sleep(2)
    ret = vmw.getVMStatus(vmobj)
    print 'VM Status is %s' % ret['state']
    if ret['state'] == 'Running' or ret['state'] == ['running']:
        print 'VM is running, now can display it.'
        break

ret = vmw.getRDPUrl(vmobj)
if ret['Result'] == 'FAIL':
    print ret['error']
    sys.exit(-1)

rdp_client_cmd = RDP_CLIENT_EXECUTE_PATH % ret['mgr_url']
commands.getoutput(rdp_client_cmd)
