#!/usr/bin/python

##################################################
# before run this script , make sure
# - python2.7 is already installed
# - tinker is already installed. if not run command below
#        sudo apt-get install python-tk

import os, sys, time, commands
from Tkinter import *
from client_sdk import *
from tkMessageBox import *

fields = 'Account', 'Password', 'Server'

def ndp_connect(ip, port):
    cmd = '/usr/bin/ndpclient -h ' + ip + ' -p ' + str(port)
    commands.getoutput(cmd)

def start_first_vm(res):
    user_id = res['Account']
    user_pw = res['Password']
    clc_ip  = res['Server']

    vmw = cloudDesktopWrapper()
    vmw.setHost(clc_ip, 80)
    vmw.setUser(user_id,  user_pw)

    if not vmw.logon():
        showerror("logon failed", "try to verify your user name & password")
        return

    # get list of vms
    list_vms = vmw.getVDList()
    vmobj = list_vms['data'][0]

    if vmobj['phase'] == 'editing':
        if vmobj['state'] == 'running' or vmobj['state'] == 'Running':
            ret = vmw.getRDPUrl(vmobj)
            if ret['Result'] == 'FAIL':
                showerror("Connect failed", ret['error'])
            else:
                protocol = ret['protocol']
                if protocol != "NDP":
                    showerror("Connect failed", "protocol is NOT NDP!")
                ndp_connect(ret['rdp_ip'], ret['rdp_port'])
            return

    ################################################
    ### step 1: create database record for this vm
    ret = vmw.startVM(vmobj)
    if ret['Result'] == 'FAIL':
        showerror("StartVM failed", ret['error'])
        vmw.errorHandle(vmobj)
        return
    else:
        vmobj['tid'] = ret['tid']

    ################################################
    ### step 2: prepare image file for this vm
    ret = vmw.prepareVM(vmobj)
    if ret['Result'] == 'FAIL':
        showerror("PrepareVM failed", ret['error'])
        vmw.errorHandle(vmobj)
        return

    while (1):
        time.sleep(2)
        ret = vmw.getPrepareProgress(vmobj)
        #print 'download progress = %s' % ret['progress']
        if ret['phase'] == 'preparing' and ret['state'] == 'done':
            break
        if ret['state'] == 'stopped':
            return

    ################################################
    ### step 3: actually run this vm
    ret = vmw.runVM(vmobj)
    if ret['Result'] == 'FAIL':
        showerror("RunVM failed", ret['error'])
        vmw.errorHandle(vmobj)
        sys.exit(-1)

    flag = False
    timer_expired = False
    while (not flag and not timer_expired):
        time.sleep(2)
        ret = vmw.getVMStatus(vmobj)
        # print 'VM Status is %s' % ret['state']
        if ret['state'] == 'Running' or ret['state'] == 'running':
            #print 'VM is running, now can display it.'
            flag = True
            break
        elif ret['state'] == 'stopped' :
            timer_expired = True

    if flag :
        ret = vmw.getRDPUrl(vmobj)
        if ret['Result'] == 'FAIL':
            showerror("Connect failed", ret['error'])
        else:
            protocol = ret['protocol'];
            if protocol != "NDP":
                showerror("Connect failed", "protocol is NOT NDP!")
            ndp_connect(ret['rdp_ip'], ret['rdp_port'])
        return

    if timer_expired:
        vmw.errorHandle(vmobj)

def fetch(entries):
   ret = {}
   for entry in entries:
      field = entry[0]
      text  = entry[1].get()
      ret[field] = text
   start_first_vm(ret)

def makeform(root, fields):
   entries = []
   for field in fields:
      row = Frame(root)
      lab = Label(row, width=15, text=field, anchor='w')
      ent = Entry(row)
      row.pack(side=TOP, fill=X, padx=5, pady=5)
      lab.pack(side=LEFT)
      ent.pack(side=RIGHT, expand=YES, fill=X)
      entries.append((field, ent))
   return entries

if __name__ == '__main__':
   root = Tk()
   ents = makeform(root, fields)
   root.bind('<Return>', (lambda event, e=ents: fetch(e)))
   b1 = Button(root, text='Login', command=(lambda e=ents: fetch(e)))
   b1.pack(side=RIGHT, padx=5, pady=5)
   root.mainloop()