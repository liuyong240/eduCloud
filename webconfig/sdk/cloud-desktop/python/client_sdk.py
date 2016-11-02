
import requests
import json

class cloudDesktopWrapper():
    def __init__(self):
        self.sessionID      = ''
        self.user_id        = ''
        self.user_password  = ''
        self.host_ip        = ''
        self.host_port      = 80

        self.login_url       = "clc/api/1.0/user_login"
        self.list_vm         = "clc/api/1.0/list_myvds"
        self.create_url      = "clc/api/1.0/rvd/create"
        self.start_url       = "clc/api/1.0/rvd/start"
        self.prepare_url     = "clc/api/1.0/rvd/prepare"
        self.progress_url    = "clc/api/1.0/rvd/getprogress"
        self.run_url         = "clc/api/1.0/rvd/run"
        self.stop_url        = "clc/api/1.0/rvd/stop"
        self.vmstatus_url    = "clc/api/1.0/rvd/getvmstatus"
        self.remove_task_url = "clc/api/1.0/tasks/delete"
        self.rdp_url         = "clc/api/1.0/rvd/get_rdp_url"
        self.del_vm_url      = "clc/api/1.0/tasks/delete"

    def setHost(self, ip, port=80):
        self.host_ip    = ip
        self.host_port  = port

    def setUser(self, user_id, user_password):
        self.user_id        = user_id
        self.user_password  = user_password

    def logon(self):
        url = 'http://%s:%s/%s' % (self.host_ip,  self.host_port, self.login_url)
        payload = {
            'email'     : self.user_id,
            'password'  : self.user_password,
        }

        r = requests.post(url, data=payload)
        result = json.loads(r.content)

        if result['status'] == 'SUCCESS':
            self.sessionID = result['sid']
            return True
        else:
            return False

    # if sucess, return as belwo
    # {
    #   'Result' : 'OK',
    #   'data'   : list of vms
    # }
    #
    # each vm in list looks like  below:
    # {
    #   'ecid'      : 'image id',
    #   'name'      : 'image name',
    #   'ostype'    : 'image os type',
    #   'desc'      : 'image description',
    #   'tid'       : 'transaction id',
    #   'phase'     : 'transaction phase',
    #   'state'     : 'transaction state',
    #   'mgr_url'   : 'RDP access ip:port'
    #   'id'        : 'index in list'
    # }
    #
    # if error, return as below
    # {
    #   'Result' : 'Failed',
    #   'error'  : 'error message'
    # }
    def getVDList(self):
        url = 'http://%s:%s/%s' % (self.host_ip,  self.host_port, self.list_vm)
        payload = {
            'user': self.user_id,
            'sid':  self.sessionID,
        }

        r = requests.post(url, data=payload)
        result = json.loads(r.content)
        return result

    ###########################################################
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##   failed :  ['Result': 'FAIL',  'error' : error msg]
    ##
    ###########################################################
    def _create_tvd(self, vmdata):
        url = 'http://%s:%s/%s/%s' % (self.host_ip,  self.host_port, self.create_url, vmdata['ecid'])
        payload = {
            'sid': self.sessionID,
        }
        r = requests.post(url, data=payload)
        result = json.loads(r.content)
        return result

    def _parseTID(self, tid):
        _tmp = tid.split(':')
        return _tmp[0], _tmp[1], _tmp[2]

    ###########################################################
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##   failed :  ['Result': 'FAIL',  'error' : error msg]
    ##
    ###########################################################
    def _start_tvd(self, vmdata):
        tid = vmdata['tid']
        srcid, dstid, insid = self._parseTID(tid)

        url = 'http://%s:%s/%s/%s/%s/%s' % (self.host_ip,  self.host_port, self.start_url, srcid, dstid, insid)
        payload = {
            'sid': self.sessionID,
        }
        r = requests.post(url, data=payload)
        result = json.loads(r.content)
        return result

    def startVM(self, vmdata):
        if vmdata['tid'] == '':
            return self._create_tvd(vmdata)
        else:
            return self._start_tvd(vmdata)

    ###########################################################
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##
    ###########################################################
    def stopVM(self, vmdata):
        tid = vmdata['tid']
        srcid, dstid, insid = self._parseTID(tid)

        url = 'http://%s:%s/%s/%s/%s/%s' % (self.host_ip,  self.host_port, self.stop_url, srcid, dstid, insid)
        payload = {
            'sid': self.sessionID,
        }
        r = requests.post(url, data=payload)
        result = json.loads(r.content)
        return result


    ###########################################################
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##   failed :  ['Result': 'FAIL',  'error' : error msg]
    ##
    ###########################################################
    def prepareVM(self, vmdata):
        tid = vmdata['tid']
        srcid, dstid, insid = self._parseTID(tid)

        url = 'http://%s:%s/%s/%s/%s/%s' % (self.host_ip,  self.host_port, self.prepare_url, srcid, dstid, insid)
        payload = {
            'sid': self.sessionID,
        }
        r = requests.post(url, data=payload)
        result = json.loads(r.content)
        return result

    ###########################################################
    ##
    ##  return = {
    ##    'type': 'taskstatus',
    ##    'phase': "preparing",
    ##    'state': 'downloading',
    ##    'progress': 0,
    ##    'tid': tid,
    ##    'prompt': '',
    ##    'errormsg': '',
    ##    'failed' : 0
    ##  }
    ##
    ###########################################################
    def getPrepareProgress(self, vmdata):
        tid = vmdata['tid']
        srcid, dstid, insid = self._parseTID(tid)

        url = 'http://%s:%s/%s/%s/%s/%s' % (self.host_ip,  self.host_port, self.progress_url, srcid, dstid, insid)
        r = requests.post(url)
        result = json.loads(r.content)
        return result

    ###########################################################
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'tid'   : tid]
    ##
    ###########################################################
    def runVM(self, vmdata):
        tid = vmdata['tid']
        srcid, dstid, insid = self._parseTID(tid)

        url = 'http://%s:%s/%s/%s/%s/%s' % (self.host_ip,  self.host_port, self.run_url, srcid, dstid, insid)
        payload = {
            'sid': self.sessionID,
        }
        r = requests.post(url, data=payload)
        result = json.loads(r.content)
        return result

    ###########################################################
    ##
    ##  return = {
    ##        'type'    : 'taskstatus',
    ##        'phase'  : "editing",
    ##        'state'  : 'stopped', 'booting', 'running' ,
    ##        'tid'    : _tid,
    ##        'failed' : 0
    ##  }
    ##
    ###########################################################
    def getVMStatus(self, vmdata):
        tid = vmdata['tid']
        srcid, dstid, insid = self._parseTID(tid)

        url = 'http://%s:%s/%s/%s/%s/%s' % (self.host_ip,  self.host_port, self.vmstatus_url, srcid, dstid, insid)
        r = requests.post(url)
        result = json.loads(r.content)
        return result

    ###########################################################
    ##
    ## return :
    ##   sucess :  ['Result': 'OK',    'mgr_url'   : rdp url]
    ##
    ###########################################################
    def getRDPUrl(self, vmdata):
        tid = vmdata['tid']
        srcid, dstid, insid = self._parseTID(tid)

        url = 'http://%s:%s/%s/%s/%s/%s' % (self.host_ip,  self.host_port, self.rdp_url, srcid, dstid, insid)
        payload = {
            'sid': self.sessionID,
        }
        r = requests.post(url, data=payload)
        result = (r.content)
        return json.loads(result)

    def delet_vm(self, vmdata):
        tid = vmdata['tid']

        url = 'http://%s:%s/%s' % (self.host_ip,  self.host_port, self.del_vm_url)
        payload = {
            'tid': tid,
        }
        r = requests.post(url, data=payload)
        result = (r.content)
        return json.loads(result)

    def errorHandle(self, vmdata):
        self.delet_vm(vmdata)