import sys, time, commands
from client_sdk import *


vmw = cloudDesktopWrapper()
vmw.setHost('192.168.96.124')
vmw.setUser('wangfeng', '11111111')

if not vmw.logon():
    print 'logon failed, try correct user name & password'
    sys.exit(-1)

# get list of vms
list_vms = vmw.getVDList()
vmobj = list_vms[0]

if vmobj['phase'] == 'editing':
    if vmobj['state'] == 'running' or vmobj['state'] == 'Running':
        vmw.stopVM(vmobj)
        time.sleep(2)

ret = vmw.startVM(vmobj)
if ret['Result'] == 'FAIL':
    print ret['error']
    sys.exit(-1)

ret = vmw.prepareVM(vmobj)
if ret['Result'] == 'FAIL':
    print ret['error']
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
    sys.exit(-1)

while (1):
    time.sleep(2)
    ret = vmw.getVMStatus(vmobj)
    print 'VM Status is %s' % ret['state']
    if ret['state'] == 'Running' or ret['running']:
        print 'VM is running, now can display it.'
        break

rdp_client_cmd = '%s %s' % ('rdesktop', vmobj['mgr_url'])
commands.getoutput(rdp_client_cmd)
