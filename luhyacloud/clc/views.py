# coding=UTF-8

from __future__ import division
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

import json
import random, pickle, pexpect, os, base64, shutil, time, datetime
import logging
import commands
from datetime import datetime

from models import *

from luhyaapi.educloudLog import *
from luhyaapi.luhyaTools import configuration
from luhyaapi.hostTools import *
from luhyaapi.settings import *
from luhyaapi.adToolWrapper import *
from sortedcontainers import SortedList
import requests, memcache
from django.utils.translation import ugettext as _

logger = getclclogger()

CC_DETAIL_TEMPLATE = \
'<div class="col-lg-6">' + \
    '<div class="list-group">' + \
        '<h3>' + _("Service Data") + '</h3>' + \
        '<p class="list-group-item">' + \
            _("Web Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.web}}</em></span>' + \
            '<!--<button type="button" id="restart_http">_("Restart")</button>-->' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Daemon Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.daemon}}</em></span>' + \
            '<!--<button type="button" id="restart_daemon">_("Restart")</button>-->' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("SSH Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.ssh}}</em></span>' + \
            '<!--<button type="button" id="restart_ssh">_("Restart")</button>-->' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("RSYNC Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.rsync}}</em></span>' + \
            '<!--<button type="button" id="restart_rsync">_("Restart")</button>-->' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("AMQP Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.amqp}}</em></span>' + \
            '<!--<button type="button" id="restart_amqp">_("Restart")</button>-->' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Memcache Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.memcache}}</em></span>' + \
            '<!--<button type="button" id="restart_memcache">_("Restart")</button>-->' + \
        '</p>' + \
        '<h3>' + _("Hardware Parameters")+ '</h3>' + \
        '<p class="list-group-item">' + \
            _("HostName") + \
            '<span class="pull-right text-muted"><em>{{host_ips.name}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Location") + \
            '<span class="pull-right text-muted"><em>{{host_ips.location}}</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '<p class="list-group-item">' + \
            _("CPU Cores") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.cpus}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("CPU Usage") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.cpu_usage}}%</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '<p class="list-group-item">' + \
            _("Total Memory") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.mem}}G</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Memory Usage") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.mem_usage}}%</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '<p class="list-group-item">' + \
            _("Total Disk") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.disk}}G</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Disk Usage") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.disk_usage}}%</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '<button id="ccres_modify" type="button" class="btn btn-primary">' + _("Network Resource Configure") + '</button>' + \
    '</div>' + \
'</div>' + \
'<div class="col-lg-6">' + \
    '<div class="list-group">' + \
        '<div style="display:none" id="ip0"> {{host_ips.ip0}}</div>' + \
        '<div style="display:none" id="mac0">{{host_ips.mac0}}</div>' + \
        '<h3>' + _("IP Addresses") + '</h3>' + \
        '<p class="list-group-item">' + \
            _("External IP Address") + \
            '<span class="pull-right text-muted"><em>{{host_ips.eip}}</em></span>' + \
            '<button type="button" id="exip_edit">' + _("Edit") + '</button>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 0") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip0}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 1") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip1}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 2") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip2}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 3") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip3}}</em></span>' + \
        '</p>' + \
        '<h3>' + _("MAC Addresses") + '</h3>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 0") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac0}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 1") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac1}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 2") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac2}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 3") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac3}}</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '{{permission_button}}' + \
    '</div>' + \
'</div>'

VM_LIST_GROUP_ITEM = \
        '<p class="list-group-item">' + \
            '{{vminfo.insid}}' + \
            '<span class="pull-right text-muted"><em>{{vminfo.state}}</em></span>' + \
            '<p class="list-group-item">' + \
            _("Guest OS") + '<span class="pull-right text-muted"><em>{{vminfo.guest_os}}</em></span>' + \
            '</p>' + \
            '<p class="list-group-item">' + \
            _("Memroy")+ '<span class="pull-right text-muted"><em>{{vminfo.mem}}G</em></span>' + \
            '</p>' + \
            '<p class="list-group-item">' + \
            _("VCPU") + '<span class="pull-right text-muted"><em>{{vminfo.vcpu}}</em></span>' + \
            '</p>' + \
        '</p>'


NC_DETAIL_TEMPLATE = \
'<div class="col-lg-6">' + \
    '<div class="list-group">' + \
        '<h3>' +_("Virtual Machine Data") + '</h3>' + \
        '{{vminfos}}' + \
        '<h3>' + _("Service Data") + '</h3>' + \
        '<p class="list-group-item">' + \
            _("Daemon Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.daemon}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("SSH Service") + \
            '<span class="pull-right text-muted"><em>{{service_data.ssh}}</em></span>' + \
        '</p>' + \
        '<h3>' +_("Hardware Parameters") + '</h3>' + \
        '<p class="list-group-item">' + \
            _("HostName") + \
            '<span class="pull-right text-muted"><em>{{host_ips.name}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Location") + \
            '<span class="pull-right text-muted"><em>{{host_ips.location}}</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '<p class="list-group-item">' + \
            _("CPU Cores") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.cpus}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("CPU Usage") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.cpu_usage}}%</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '<p class="list-group-item">' + \
            _("Total Memory") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.mem}}G</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Memory Usage") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.mem_usage}}%</em></span>' + \
        '</p>' + \
        '<p></p>' + \
        '<p class="list-group-item">' + \
            _("Total Disk") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.disk}}G</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("Disk Usage") + \
            '<span class="pull-right text-muted"><em>{{hardware_data.disk_usage}}%</em></span>' + \
        '</p>' + \
    '</div>' + \
'</div>' + \
'<div class="col-lg-6">' + \
    '<div class="list-group">' + \
        '<div style="display:none" id="ip0"> {{host_ips.ip0}}</div>' + \
        '<div style="display:none" id="mac0">{{host_ips.mac0}}</div>' + \
        '<h3>' + _("IP Addresses") + '</h3>' + \
        '<p class="list-group-item">' + \
            _("External IP Address") + \
            '<span class="pull-right text-muted"><em>{{host_ips.eip}}</em></span>' + \
            '<button type="button" id="exip_edit">' + _("Edit") + '</button>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 0") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip0}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 1") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip1}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 2") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip2}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("IP Address 3") + \
            '<span class="pull-right text-muted"><em>{{host_ips.ip3}}</em></span>' + \
        '</p>' + \
        '<h3>' + _("MAC Addresses") + '</h3>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 0") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac0}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 1") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac1}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 2") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac2}}</em></span>' + \
        '</p>' + \
        '<p class="list-group-item">' + \
            _("MAC Address 3") + \
            '<span class="pull-right text-muted"><em>{{host_ips.mac3}}</em></span>' + \
        '</p>' + \
        '<p></p>' + \
    '</div>' + \
'</div>'


''' Example of nc status data in memcache
{
    "net_data": {
        "exip": "192.168.96.127",
        "ip2": "",
        "ip0": "192.168.96.127",
        "ip1": "192.168.56.1",
        "mac3": "",
        "mac2": "",
        "mac1": "0A:00:27:00:00:00",
        "ip3": "",
        "mac0": "84:2B:2B:48:CF:06"
    },
    "nid": "nc#84:2B:2B:48:CF:06#status",
    "vm_data": [
        {"mem": 4, "vcpu": 2, "uuid": "41cbbb16-2b74-428b-a01b-7ff8a08c6dd3", "insid": "a", "guest_os": "Ubuntu (64 bit)"},
        {"mem": 4, "vcpu": 2, "uuid": "2999ccde-ec4a-47d7-a6dd-fdbc24ae9915", "insid": "b", "guest_os": "Ubuntu (64 bit)"},
        {"mem": 12, "vcpu": 1, "uuid": "cbc86361-23b5-40ce-b131-c654b5215cb4", "insid": "c", "guest_os": "Ubuntu (64 bit)"}
    ],
    "service_data": {
        "web": "Running",
        "rsync": "Running",
        "amqp": "Running",
        "daemon": "Closed",
        "memcache": "Running",
        "ssh": "Running"
    },
    "hardware_data": {
        "disk_usage": 11.1,
        "mem": 32,
        "cpus": 16,
        'cpu_usage': 14.9,
        "mem_usage": 24.8,
        "disk": 236
    },
    "type": "nodestatus"
}
'''

def getPhyServerStatusFromMC(stype, mac):
    payload = None
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    key = str('%s#%s#status' % (stype, mac))
    try:
        payload = mc.get(key)
        if payload != None:
            payload = json.loads(payload)
            payload = payload['hardware_data']
    except Exception as e:
        logger.error("--- getPhyServerStatusFromMC error = %s" % str(e))

    return payload

def get_nc_avail_res(nc_mac):
    total_res = {}

    used_res  = {}
    used_res['cpu']  = 0
    used_res['mem']  = 0
    used_res['disk'] = 0

    reported_avail_res = {}
    computed_avail_res = {}

    final_avail_res    = {
        '1mem'       : 0,
        '2cpu_usage' : 0,
        '3disk'      : 0,
        '4cpu'       : 0,
    }

    data = getPhyServerStatusFromMC('nc', nc_mac)

    if data == None:
        pass
    else:
        total_res['cpu']                = data['cpus']
        total_res['mem']                = data['mem']
        total_res['disk']               = data['disk']

        final_avail_res['2cpu_usage']    = 100 - data['cpu_usage']
        final_avail_res['3disk']         = data['disk'] * (1 - data['disk_usage'] / 100.0)

        reported_avail_res['mem'] = data['mem']  * (1 - data['mem_usage']  / 100.0)

        # get allocate but not used yet res
        ncobj = ecServers.objects.get(mac0=nc_mac, role='nc')
        trecs = ectaskTransaction.objects.filter(ncip = ncobj.ip0)
        if trecs.count() > 0:
            for trec in trecs:
                runtime_option = json.loads(trec.runtime_option)
                used_res['cpu']  += runtime_option['cpus']
                used_res['mem']  += runtime_option['memory']

        computed_avail_res['cpu']   = total_res['cpu']  - used_res['cpu']
        computed_avail_res['mem']   = total_res['mem']  - used_res['mem']

        final_avail_res['4cpu'] = computed_avail_res['cpu']
        final_avail_res['1mem'] = min(computed_avail_res['mem'], reported_avail_res['mem'])

    return final_avail_res

def findVMRunningResource(request, insid):
    ua_admin = ecAccount.objects.get(userid=request.user)
    ua_admin_role_value = ecAuthPath.objects.get(ec_authpath_name = ua_admin.ec_authpath_name)
    role_prefix = ua_admin_role_value.ec_authpath_value.split('.admin')[0]

    l = SortedList()

    _ccip = None
    _ncip = None
    _msg  = "Can't Find appropriate cluster machine and node machine ."

    if insid.find('VD') == 0:
        vmrec = ecVDS.objects.get(insid=insid)
        filter = 'rvd'
        vm_res_matrix = get_desktop_res()
        vm_res_matrix['mem'] += vmrec.memory

    if insid.find('VS') == 0:
        vmrec = ecVSS.objects.get(insid=insid)
        filter = 'vs'
        vm_res_matrix = get_server_res()
        vm_res_matrix['mem'] += vmrec.memory

    logger.error('vm_res_matrix for %s is  %s' % (insid, json.dumps(vm_res_matrix)))

    cc_def = vmrec.cc_def
    nc_def = vmrec.nc_def

    if cc_def == 'any':
        if is_vd_allowed_in_vscc() == True:
            ccs = ecCCResources.objects.filter()
        else:
            ccs = ecCCResources.objects.filter(cc_usage=filter)
    else:
        ccs = ecCCResources.objects.filter(ccname=cc_def)

    for cc in ccs:
        ccobj = ecServers.objects.get(ccname=cc.ccname, role='cc')

        # add permission check here for those admin
        sobjs = ecServers_auth.objects.filter(srole='cc', mac0=ccobj.mac0, role_value__contains=role_prefix)
        if sobjs.count() == 0:
            continue

        if nc_def == 'any':
            ncs = ecServers.objects.filter(ccname=cc.ccname, role='nc')
            for nc in ncs:
                if nc.hypervisor == vmrec.hypervisor:
                    final_avail_res = get_nc_avail_res(nc.mac0)
                    final_avail_res['xncip'] = nc.ip0
                    final_avail_res['xccip'] = ccobj.ip0
                    l.add(final_avail_res)
        else:
            ncobj = ecServers.objects.get(ccname=cc.ccname, ip0=nc_def, role='nc')
            final_avail_res = get_nc_avail_res(ncobj.mac0)
            final_avail_res['xncip'] = ncobj.ip0
            final_avail_res['xccip'] = ccobj.ip0
            l.add(final_avail_res)

    # now check sorted nc to find best one
    end = len(l)
    for index in range(0, end):
        data = l[end - index -1]
        if data['1mem']         > vm_res_matrix['mem']          and \
           data['2cpu_usage']   > vm_res_matrix['cpu_usage']    and \
           data['3disk']        > vm_res_matrix['disk']:
            _ccip = data['xccip']
            _ncip = data['xncip']
            _msg = ''
            logger.error("get best node : ip = %s" % _ncip)
            break;
        else:
            _msg = (_('available nc resource is ') + '%s' + _(', but required is ') + '%s') % (json.dumps(data), json.dumps(vm_res_matrix))
            logger.error(_msg)
    return _ccip, _ncip, _msg

def findBuildResource(srcid):

    l = SortedList()

    _ccip = None
    _ncip = None
    _msg  = _("Can't Find appropriate cluster machine and node machine .")

    # get the expected usage of cc
    rec = ecImages.objects.get(ecid=srcid)
    if rec.img_usage == "server":
        filter = 'vs'
        vm_res_matrix = get_server_res()
        vmtypeobj = ecVMTypes.objects.get(name='vssmall')
        vm_res_matrix['mem'] += vmtypeobj.memory
    else:
        filter = 'rvd'
        vm_res_matrix = get_desktop_res()
        logger.error("origin resource request is %s" % json.dumps(vm_res_matrix))
        vmtypeobj = ecVMTypes.objects.get(name='vdsmall')
        vm_res_matrix['mem'] += vmtypeobj.memory
        logger.error("rvd resource request is %s" % json.dumps(vm_res_matrix))

    logger.error('vm_res_matrix for %s is  %s' % (srcid, json.dumps(vm_res_matrix)))

    # get a list of cc
    if is_vd_allowed_in_vscc() == True:
        ccs = ecCCResources.objects.filter()
    else:
        ccs = ecCCResources.objects.filter(cc_usage=filter)

    # for each cc, find a good candidate nc and return, based on data in memcache
    # and compare all these selected ncs, find the best one
    for cc in ccs:
        # get list of ncs
        ccobj = ecServers.objects.get(ccname=cc.ccname, role='cc')
        ncs   = ecServers.objects.filter(ccname=cc.ccname , role='nc')
        for nc in ncs:
            if nc.hypervisor == rec.hypervisor:
                final_avail_res = get_nc_avail_res(nc.mac0)
                final_avail_res['xncip'] = nc.ip0
                final_avail_res['xccip'] = ccobj.ip0
                l.add(final_avail_res)

    end = len(l)
    for index in range(0, end):
        data = l[end - index -1]
        if data['1mem']         > vm_res_matrix['mem']          and \
           data['2cpu_usage']   > vm_res_matrix['cpu_usage']    and \
           data['3disk']        > vm_res_matrix['disk']:
            _ccip = data['xccip']
            _ncip = data['xncip']
            _msg = ''
            logger.error("get best node : ip = %s" % _ncip)
            break;
        else:
            _msg = (_('available nc resource is ') + '%s' + _(', but required is ') + '%s') % (json.dumps(data), json.dumps(vm_res_matrix))
            logger.error(_msg)
    return _ccip, _ncip, _msg

def display_login_window(request):
    return render(request, 'clc/login.html', {})

def isAdmin(user):
    u = ecAccount.objects.get(userid = user.username)
    role_name = u.ec_authpath_name
    role_value = ecAuthPath.objects.get(ec_authpath_name = role_name)
    return role_value.ec_authpath_value.endswith('.admin')


def user_login(request):
    response = {}
    username = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if not user.is_active:
            response['status'] = "FAILURE"
            response['reason'] = _("account is not activated.")
            return HttpResponse(json.dumps(response), content_type='application/json')

        if isAdmin(user):
            response['status'] = "FAILURE"
            response['reason'] = _("Admin is NOT allowd to login")
            return HttpResponse(json.dumps(response), content_type='application/json')

        login(request, user)
        response['status'] = "SUCCESS"
        response['url'] = "/portal/cloud-desktops"
        response['sid'] = request.session.session_key
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        # Return an 'invalid login' error message.
        response['status'] = "FAILURE"
        response['reason'] = _("account is invalid")
        return HttpResponse(json.dumps(response), content_type='application/json')

def admin_login(request):
    response = {}
    username = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if not user.is_active:
            response['status'] = "FAILURE"
            response['reason'] = _("account is not activated.")
            return HttpResponse(json.dumps(response), content_type='application/json')

        if not isAdmin(user):
            response['status'] = "FAILURE"
            response['reason'] = _("Only Admin is allowd to login")
            return HttpResponse(json.dumps(response), content_type='application/json')

        login(request, user)
        response['status'] = "SUCCESS"
        response['url'] = "/clc/images"
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        # Return an 'invalid login' error message.
        response['status'] = "FAILURE"
        response['reason'] = _("account is invalid")
        return HttpResponse(json.dumps(response), content_type='application/json')

def user_logout(request):
    logout(request)
    return render(request, 'portal/index.html', {})


##########################################################################
# Account Management
##########################################################################
@login_required(login_url='/portal/admlogin')
def adm_add_new_account(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    role_prefix = ua_role_value.ec_authpath_value.split('.admin')[0]

    authnamelist =  ecAuthPath.objects.all()
    roles = []

    for authname in authnamelist:
        if authname.ec_authpath_value.startswith(role_prefix):
            roles.append(authname.ec_authpath_name)

    context = {
        'roles': roles,
    }
    return render(request, 'clc/form/adm_add_new_account.html', context)

@login_required(login_url='/portal/admlogin')
def account_create(request):
    response = {}
    # create a new account
    # 1. check if user already existed
    num = User.objects.filter(username=request.POST['userid']).count()
    if num > 0 :
        response['Result'] = 'FAIL'
        response['errormsg'] = 'duplicated user name.'
        return HttpResponse(json.dumps(response), content_type="application/json")

    # 2. start to create new account
    user = User.objects.create_user(request.POST['userid'], request.POST['email'], request.POST['password'])
    # create ecAccount record
    _vdparar = {}
    _vdparar['pds'] = request.POST['pds']
    _vdparar['sds'] = request.POST['sds']
    _vdparar['vapp'] = request.POST['vapp']
    rec = ecAccount(
        userid  = request.POST['userid'],
        showname = request.POST['displayname'],
        ec_authpath_name = request.POST['role'],
        phone = request.POST['phone'],
        description = request.POST['desc'],
        vdpara=json.dumps(_vdparar),
    )
    rec.save()
    addUserPrvDataDir(request.POST['userid'])

    if _vdparar['vapp'] == 'yes':
        virtapp_addAccount2AD(request.POST['userid'], request.POST['password'])

    response['Result'] = 'OK'
    return HttpResponse(json.dumps(response), content_type="application/json")

@login_required(login_url='/portal/admlogin')
def admin_batch_add_new_accounts(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    role_prefix = ua_role_value.ec_authpath_value.split('.admin')[0]

    authnamelist =  ecAuthPath.objects.all()
    roles = []

    for authname in authnamelist:
        if authname.ec_authpath_value.startswith(role_prefix):
            roles.append(authname.ec_authpath_name)

    context = {
        'roles': roles,
    }
    return render(request, 'clc/form/adm_add_new_account_batch.html', context)

@login_required(login_url='/portal/admlogin')
def account_create_batch(request):
    response = {}
    prefix = request.POST['prefix']
    id_start = int(request.POST['id_start'])
    id_end = int(request.POST['id_end'])
    password = request.POST['password']
    role = request.POST['role']
    email = request.POST['email']
    phone = request.POST['phone']
    desc = request.POST['desc']
    _vdparar = {}
    _vdparar['pds'] = request.POST['pds']
    _vdparar['sds'] = request.POST['sds']
    _vdparar['vapp'] = request.POST['vapp']

    # construct user list
    user_list = []
    for index in range(id_start, id_end):
        newname = prefix + str(index)
        user_list.append(newname)
        # check existence
        num = User.objects.filter(username=newname).count()
        if num > 0:
            response['Result'] = 'FAIL'
            response['errormsg'] = _('duplicated user name: ') + newname
            return HttpResponse(json.dumps(response), content_type="application/json")

    for u in user_list:
        user = User.objects.create_user(u, email, password)
        rec = ecAccount(
            userid  = u,
            showname = u,
            ec_authpath_name = role,
            phone = phone,
            description = desc,
            vdpara=json.dumps(_vdparar),
        )
        rec.save()
        addUserPrvDataDir(u)

        if _vdparar['vapp'] == 'yes':
            virtapp_addAccount2AD(u, password)

    response['Result'] = 'OK'
    return HttpResponse(json.dumps(response), content_type="application/json")

def request_new_account(request):
    context = {}
    return render(request, 'clc/form/request_new_account.html', context)

def account_request(request):
    userid = request.POST['userid']
    displayname = request.POST['displayname']
    password = request.POST['password']
    email = request.POST['email']
    phone = request.POST['phone']
    desc = request.POST['desc']

    response = {}
    # create a new account
    # 1. check if user already existed
    num = User.objects.filter(username=userid).count()
    if num > 0 :
        response['Result'] = 'FAIL'
        response['errormsg'] = _('duplicated user name.')
        return HttpResponse(json.dumps(response), content_type="application/json")

    # 2. start to create new account
    user = User.objects.create_user(userid, email, password)
    user.is_active = 0
    user.save()

    _vdpara = {}
    _vdpara['pds'] = 0
    _vdpara['sds'] = "no"
    _vdpara['vapp'] = "no"

    # create ecAccount record
    rec = ecAccount(
        userid  = userid,
        showname = displayname,
        phone = phone,
        description = desc,
        vdpara=json.dumps(_vdpara),
    )
    rec.save()

    response['Result'] = 'OK'
    return HttpResponse(json.dumps(response), content_type="application/json")

@login_required(login_url='/portal/admlogin')
def restore_password(request):
    context = {}
    return render(request, 'clc/form/restore_password.html', context)

@login_required(login_url='/portal/admlogin')
def send_feedback(request):
    context = {}
    return render(request, 'clc/form/send_feedback.html', context)

@login_required(login_url='/portal/admlogin')
def edit_profile(request, uid):
    u = User.objects.get(username=uid)
    ua = ecAccount.objects.get(userid=uid)

    _user = {}
    _user['userid'] = ua.userid
    _user['showname'] = ua.showname
    _user['role'] = ua.ec_authpath_name
    _user['email'] = u.email
    _user['phone'] = ua.phone
    _user['desc'] = ua.description

    if len(ua.vdpara) > 0:
        _vdpara = json.loads(ua.vdpara)
        _user['pds'] = _vdpara['pds']
        _user['sds'] = _vdpara['sds']
    else:
        _user['pds'] = ''
        _user['sds'] = ''

    authnamelist =  ecAuthPath.objects.all()
    roles = []

    for authname in authnamelist:
        roles.append(authname.ec_authpath_name)

    context = {
        'user': _user,
        'roles': roles,
    }
    return render(request, 'clc/form/update_account_profile.html', context)

@login_required(login_url='/portal/admlogin')
def account_update_profile(request):
    u = User.objects.get(username=request.POST['userid'])
    ua = ecAccount.objects.get(userid=request.POST['userid'])

    u.email = request.POST['email']
    ua.phone = request.POST['phone']
    ua.showname = request.POST['displayname']
    ua.description = request.POST['desc']

    u.save()
    ua.save()

    response = {}
    response['Result'] = 'OK'
    return HttpResponse(json.dumps(response), content_type="application/json")

@login_required(login_url='/portal/admlogin')
def edit_password(request, uid):
    context = {
        'uid': uid,
    }
    return render(request, 'clc/form/reset_account_password.html', context)

@login_required(login_url='/portal/admlogin')
def activate_user(request, uid):
    ua = ecAccount.objects.get(userid=uid)
    if ua.ec_authpath_name == '':
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _('user Role MUST be set before approved.'),
            'suggestion'    : _('Please edit user\'s role first'),
        }
        return render(request, 'clc/error.html', context)
    else:
        u = User.objects.get(username=uid)
        u.is_active = 1
        u.save()
        addUserPrvDataDir(uid)

        Message =  _('user')+ (' %s ' % uid) +  _('is activated now.')
        return HttpResponse(Message, content_type="application/json; charset=utf-8")

@login_required(login_url='/portal/admlogin')
def account_reset_password(request):
    uid = request.POST['userid']
    oldpw = request.POST['oldpassword']
    newpw = request.POST['newpassword']

    # verify old password
    response = {}
    user = authenticate(username=uid, password=oldpw)
    if user is not None:
         # set new password
        user.set_password(newpw)
        user.save()

        ua = ecAccount.objects.get(userid=request.POST['userid'])
        _vdpara = json.loads(ua.vdpara)
        if _vdpara['vapp'] == 'yes':
            virtapp_setPassword2AD(uid, newpw)

        response['Result'] = "OK"
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        # Return an 'invalid login' error message.
        response['Result'] = "FAILURE"
        response['errormsg'] = _("Password is not correct!")
        return HttpResponse(json.dumps(response), content_type='application/json')

##########################################################################
##########################################################################

@login_required(login_url='/portal/admlogin')
def index_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)
    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("System Run-time Status Overview"),
    }
    return render(request, 'clc/overview.html', context)

@login_required(login_url='/portal/admlogin')
def accounts_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Account Management"),
        'role'      : ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/accounts.html', context)

@login_required(login_url='/portal/admlogin')
def images_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Images Management"),
        'role':  ua_role_value.ec_authpath_value,
    }

    return render(request, 'clc/images.html', context)

def getCloudStatisticData():
    result = {}
    result['num_clusters'] = ecServers.objects.filter(role='cc').count()
    result['num_nodes']  =  ecServers.objects.filter(role='nc').count()
    result['num_lnodes']  = ecServers.objects.filter(role='lnc').count()
    result['num_terminals']  = ecTerminal.objects.all().count()
    result['num_accounts']  = ecAccount.objects.all().count()
    result['num_images']  = ecImages.objects.all().count()
    result['num_def_vss']  = ecVSS.objects.all().count()
    result['num_def_vd']   = ecVDS.objects.all().count()

    result['num_online_user']  = 0
    result['num_run_vss']  = 0
    result['num_run_vd']  = 0
    result['num_run_lvd']  = 0

    return result;

def getHostIPs(hrole, hmac0):
    result = {}

    if hmac0 == "":
        obj = ecServers.objects.get(role=hrole)
    else:
        obj = ecServers.objects.get(role=hrole, mac0=hmac0)

    result['name'] = obj.name
    result['location'] = obj.location
    result['eip'] = obj.eip
    result['ip0'] = obj.ip0
    result['ip1'] = obj.ip1
    result['ip2'] = obj.ip2
    result['ip3'] = obj.ip3
    result['mac0'] = obj.mac0
    result['mac1'] = obj.mac1
    result['mac2'] = obj.mac2
    result['mac3'] = obj.mac3

    return result

@login_required(login_url='/portal/admlogin')
def clc_mgr_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    cloud_data = getCloudStatisticData()
    host_ips = getHostIPs("clc", "")

    service_data    = remote_getServiceStatus("127.0.0.1", "clc")
    hardware_data   = remote_getHostHardware("127.0.0.1")

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Cloud Control Management"),
        'cloud_data' : cloud_data,
        'service_data': service_data,
        'hardware_data': hardware_data,
        'host_ips': host_ips,
        'role' : ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/clc_mgr.html', context)

@login_required(login_url='/portal/admlogin')
def edit_eip_view(request, role, mac):
    s = ecServers.objects.get(role=role, mac0=mac)
    context = {
        'role':  role,
        'eip':   s.eip,
        'mac0':  mac,
    }
    return render(request, 'clc/form/edit_eip.html', context)

def remote_getServiceStatus(ip, role):
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/machine/get_service_status' % ip
    else:
        url = 'http://%s/machine/get_service_status' % ip
    payload = {
        "role": role,
    }
    r = requests.post(url, data=payload)
    return json.loads(r.content)

def remote_getHostHardware(ip):
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/machine/get_hardware_status' % ip
    else:
        url = 'http://%s/machine/get_hardware_status' % ip
    payload = {
    }
    r = requests.post(url, data=payload)
    return json.loads(r.content)

@login_required(login_url='/portal/admlogin')
def walrus_mgr_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    wobj = ecServers.objects.get(role="walrus")
    if DoesServiceExist(wobj.ip0, 80) == "Running" :
        sip = wobj.ip0
    else:
        sip = wobj.eip

    service_data    = remote_getServiceStatus(sip, "walrus")
    hardware_data   = remote_getHostHardware(sip)
    host_ips        = getHostIPs("walrus", "")

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Cloud Walrus Management"),
        'service_data': service_data,
        'hardware_data': hardware_data,
        'host_ips': host_ips,
        'role' : ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/walrus_mgr.html', context)

@login_required(login_url='/portal/admlogin')
def cc_mgr_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Cloud Cluster Management"),
    }
    return render(request, 'clc/cc_mgr.html', context)

@login_required(login_url='/portal/admlogin')
def cc_mgr_ccname(request, ccname):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    ccobj = ecServers.objects.get(role="cc", ccname=ccname)
    if DAEMON_DEBUG == False:
        port = 80
    else:
        port = 8000
    if DoesServiceExist(ccobj.ip0, port) == "Running" :
        sip = ccobj.ip0
    else:
        sip = ccobj.eip

    service_data    = remote_getServiceStatus(sip, "cc")
    hardware_data   = remote_getHostHardware(sip)
    host_ips        = getHostIPs("cc", ccobj.mac0)

    htmlstr = CC_DETAIL_TEMPLATE
    htmlstr = htmlstr.replace('{{service_data.web}}',     service_data['web'])
    htmlstr = htmlstr.replace('{{service_data.daemon}}',  service_data['daemon'])
    htmlstr = htmlstr.replace('{{service_data.ssh}}',     service_data['ssh'])
    htmlstr = htmlstr.replace('{{service_data.rsync}}',   service_data['rsync'])
    htmlstr = htmlstr.replace('{{service_data.amqp}}',    service_data['amqp'])
    htmlstr = htmlstr.replace('{{service_data.memcache}}', service_data['memcache'])

    htmlstr = htmlstr.replace('{{host_ips.name}}',        host_ips['name'])
    htmlstr = htmlstr.replace('{{host_ips.location}}',    host_ips['location'])

    htmlstr = htmlstr.replace('{{hardware_data.cpus}}',        str(hardware_data['cpus']))
    htmlstr = htmlstr.replace('{{hardware_data.cpu_usage}}',   str(hardware_data['cpu_usage']))
    htmlstr = htmlstr.replace('{{hardware_data.mem}}',         str(hardware_data['mem']))
    htmlstr = htmlstr.replace('{{hardware_data.mem_usage}}',   str(hardware_data['mem_usage']))

    htmlstr = htmlstr.replace('{{hardware_data.disk}}',        str(hardware_data['disk']))
    htmlstr = htmlstr.replace('{{hardware_data.disk_usage}}',  str(hardware_data['disk_usage']))

    htmlstr = htmlstr.replace('{{host_ips.eip}}', host_ips['eip'])
    htmlstr = htmlstr.replace('{{host_ips.ip0}}', host_ips['ip0'])
    htmlstr = htmlstr.replace('{{host_ips.ip1}}', host_ips['ip1'])
    htmlstr = htmlstr.replace('{{host_ips.ip2}}', host_ips['ip2'])
    htmlstr = htmlstr.replace('{{host_ips.ip3}}', host_ips['ip3'])

    htmlstr = htmlstr.replace('{{host_ips.mac0}}', host_ips['mac0'])
    htmlstr = htmlstr.replace('{{host_ips.mac1}}', host_ips['mac1'])
    htmlstr = htmlstr.replace('{{host_ips.mac2}}', host_ips['mac2'])
    htmlstr = htmlstr.replace('{{host_ips.mac3}}', host_ips['mac3'])

    pbt = '<button id="permission" type="button" class="btn btn-primary">' + _("Edit Permission") + '</button>'
    if ua_role_value.ec_authpath_value == 'eduCloud.admin':
        htmlstr = htmlstr.replace('{{permission_button}}', pbt)
    else:
        htmlstr = htmlstr.replace('{{permission_button}}', '')

    response = {}
    response['Result'] = 'OK'
    response['data'] = htmlstr
    return HttpResponse(json.dumps(response), content_type="application/json")

@login_required(login_url='/portal/admlogin')
def nc_mgr_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Cloud Node Management"),
    }
    return render(request, 'clc/nc_mgr.html', context)

@login_required(login_url='/portal/admlogin')
def nc_mgr_mac(request, ccname, mac):
    logger.error("enter nc_mgr_mac --- --- ")

    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    key = str("nc#" + mac + "#status")

    try:
        payload = mc.get(key)
        if payload == None:
            pass
        else:
            payload = json.loads(payload)
            service_data = payload['service_data']
            hardware_data = payload['hardware_data']
            host_ips = getHostIPs('nc', mac)

            if 'vm_data' in payload.keys():
                vminfo = payload['vm_data']
            else:
                vminfo = []
    except Exception as e:
        payload = None

    if payload == None:
        logger.error("not get nc[%s] status data from memcache." % mac)
        response = {}
        response['Result'] = 'OK'
        response['data'] = _('<div class="col-lg-6"><p>detail information is NOT available.</p></div>')
        return HttpResponse(json.dumps(response), content_type="application/json")

    htmlstr = NC_DETAIL_TEMPLATE
    vmstr   = VM_LIST_GROUP_ITEM

    if vminfo != []:
        vms = ""
        for vm in vminfo:
            _vm = vmstr.replace('{{vminfo.insid}}',  vm['insid'])
            _vm = _vm.replace('{{vminfo.guest_os}}', vm['guest_os'])
            _vm = _vm.replace('{{vminfo.mem}}',      str(vm['mem']))
            _vm = _vm.replace('{{vminfo.vcpu}}',     str(vm['vcpu']))
            _vm = _vm.replace('{{vminfo.state}}',    vm['state'])
            vms = vms + _vm

        htmlstr = htmlstr.replace('{{vminfos}}',  vms)
    else:
        novmstr = _('''
                <p class="list-group-item">
                No VMs Information available
                </p>
        ''')
        htmlstr = htmlstr.replace('{{vminfos}}',  novmstr)

    htmlstr = htmlstr.replace('{{service_data.daemon}}',  service_data['daemon'])
    htmlstr = htmlstr.replace('{{service_data.ssh}}',     service_data['ssh'])

    htmlstr = htmlstr.replace('{{host_ips.name}}',        host_ips['name'])
    htmlstr = htmlstr.replace('{{host_ips.location}}',    host_ips['location'])

    htmlstr = htmlstr.replace('{{hardware_data.cpus}}',        str(hardware_data['cpus']))
    htmlstr = htmlstr.replace('{{hardware_data.cpu_usage}}',   str(hardware_data['cpu_usage']))

    htmlstr = htmlstr.replace('{{hardware_data.mem}}',         str(hardware_data['mem']))
    htmlstr = htmlstr.replace('{{hardware_data.mem_usage}}',   str(hardware_data['mem_usage']))

    htmlstr = htmlstr.replace('{{hardware_data.disk}}',        str(hardware_data['disk']))
    htmlstr = htmlstr.replace('{{hardware_data.disk_usage}}',  str(hardware_data['disk_usage']))

    htmlstr = htmlstr.replace('{{host_ips.eip}}', host_ips['eip'])
    htmlstr = htmlstr.replace('{{host_ips.ip0}}', host_ips['ip0'])
    htmlstr = htmlstr.replace('{{host_ips.ip1}}', host_ips['ip1'])
    htmlstr = htmlstr.replace('{{host_ips.ip2}}', host_ips['ip2'])
    htmlstr = htmlstr.replace('{{host_ips.ip3}}', host_ips['ip3'])

    htmlstr = htmlstr.replace('{{host_ips.mac0}}', host_ips['mac0'])
    htmlstr = htmlstr.replace('{{host_ips.mac1}}', host_ips['mac1'])
    htmlstr = htmlstr.replace('{{host_ips.mac2}}', host_ips['mac2'])
    htmlstr = htmlstr.replace('{{host_ips.mac3}}', host_ips['mac3'])

    response = {}
    response['Result'] = 'OK'
    response['data'] = htmlstr
    return HttpResponse(json.dumps(response), content_type="application/json")

@login_required(login_url='/portal/admlogin')
def lnc_mgr_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Cloud Local Node Management"),
    }
    return render(request, 'clc/lnc_mgr.html', context)

@login_required(login_url='/portal/admlogin')
def terminal_mgr_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Cloud Terminal Management"),
    }
    return render(request, 'clc/tnc_mgr.html', context)

@login_required(login_url='/portal/admlogin')
def hosts_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Hosts Management"),
    }
    return render(request, 'clc/hosts.html', context)

@login_required(login_url='/portal/admlogin')
def settings_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("System Settings Management"),
    }
    return render(request, 'clc/settings.html', context)

@login_required(login_url='/portal/admlogin')
def vss_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Cloud Server Management"),
    }

    return render(request, 'clc/vss.html', context)

@login_required(login_url='/portal/admlogin')
def rvds_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Remote Cloud Desktop Management"),
    }

    return render(request, 'clc/rvds.html', context)

@login_required(login_url='/portal/admlogin')
def lvds_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Local Cloud Desktop Management"),
    }

    return render(request, 'clc/lvds.html', context)

@login_required(login_url='/portal/admlogin')
def tasks_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Tasks Management"),
    }

    return render(request, 'clc/tasks.html', context)

@login_required(login_url='/portal/admlogin')
def tools_view(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)

    imageList = ecImages.objects.only("ecid")
    server_images = []
    for imgobj in imageList:
        server_images.append(imgobj.ecid)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("Administrator Tools"),
    }

    return render(request, 'clc/tools.html', context)

def handle_uploaded_file(f, chunk, filename):
    """
    Here you can do whatever you like with your files, like resize them if they
    are images
    :param f: the file
    :param chunk: number of chunk to save
    """
    if int(chunk) > 0:
        #opens for append
        _file = open(filename, 'a')
    else:
        #erases content
        _file = open(filename, 'w')

    if f.multiple_chunks:
        for chunk in f.chunks():
            _file.write(chunk)
    else:
        _file.write(f.read())

def tools_image_upload(request):
    if request.method == 'POST' and request.FILES:
        path = request.POST['image_path']
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)

        for _file in request.FILES:
            handle_uploaded_file(request.FILES[_file],
                                 request.POST['chunk'],
                                 'machine')
        #response only to notify plUpload that the upload was successful
        return HttpResponse()
    else:
        raise Http404

def tools_file_upload(request):
    root_dir = '/storage/space/software/'

    if request.method == 'POST' and request.FILES:

        rpath = request.POST['full_path'].split(',')
        for _rpath in rpath:
            root_dir =os.path.join(root_dir, _rpath)

        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        os.chdir(root_dir)

        for _file in request.FILES:
            handle_uploaded_file(request.FILES[_file],
                                 request.POST['chunk'],
                                 request.POST['name'])
        #response only to notify plUpload that the upload was successful
        return HttpResponse()
    else:
        raise Http404

def tools_list_dir_software(request):
    ret = []
    root_dir = '/storage/space/software/'

    if "full_path" in request.POST.keys():
        rpath = request.POST['full_path'].split(',')
        for _rpath in rpath:
            root_dir =os.path.join(root_dir, _rpath)

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    for name in os.listdir(root_dir):
        node = {}
        if os.path.isdir(os.path.join(root_dir, name)):
            node['name'] = name
            node['isParent'] = "true"
        else:
            node['name'] = name
        ret.append(node)

    return HttpResponse(json.dumps(ret), content_type="application/json")

def tools_list_dir_prv_data(request, uid):
    ret = []
    root_dir = '/storage/space/prv-data/%s' % uid

    if "full_path" in request.POST.keys():
        rpath = request.POST['full_path'].split(',')
        for _rpath in rpath:
            root_dir =os.path.join(root_dir, _rpath)

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    for name in os.listdir(root_dir):
        node = {}
        if os.path.isdir(os.path.join(root_dir, name)):
            node['name'] = name
            node['isParent'] = "true"
        else:
            node['name'] = name
        ret.append(node)

    return HttpResponse(json.dumps(ret), content_type="application/json")

def tools_prv_upload(request, uid):
    root_dir = '/storage/space/prv-data/%s' % uid

    if request.method == 'POST' and request.FILES:

        rpath = request.POST['full_path'].split(',')
        for _rpath in rpath:
            root_dir =os.path.join(root_dir, _rpath)

        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        os.chdir(root_dir)

        for _file in request.FILES:
            handle_uploaded_file(request.FILES[_file],
                                 request.POST['chunk'],
                                 request.POST['name'])
        #response only to notify plUpload that the upload was successful
        return HttpResponse()
    else:
        raise Http404

def software_operation(request):
    op   = request.POST['cmd']
    opt  = request.POST['opt']

    root_dir = '/storage/space/software/'

    if op == 'rm':
        arg1 = request.POST['arg1'].split(',')
        for _arg1 in arg1:
            root_dir =os.path.join(root_dir, _arg1)

        cmdline = '%s %s %s' % (op, opt, root_dir)
        execute_cmd(cmdline, False)
    elif op == 'mv':
        fdir =  root_dir
        arg1 = request.POST['arg1'].split(',')
        for _arg1 in arg1:
            fdir =os.path.join(fdir, _arg1)

        ddir =  root_dir
        arg2 = request.POST['arg2'].split(',')
        for _arg2 in arg2:
            ddir =os.path.join(ddir, _arg2)

        cmdline = '%s %s %s' % (op, fdir, ddir)
        execute_cmd(cmdline, False)

    ret={}
    ret['Result'] = 'OK'
    return HttpResponse(json.dumps(ret), content_type="application/json")


def prv_data_operation(request, uid):
    op   = request.POST['cmd']
    opt  = request.POST['opt']

    root_dir = '/storage/space/prv-data/%s' % uid

    if op == 'rm':
        arg1 = request.POST['arg1'].split(',')
        for _arg1 in arg1:
            root_dir =os.path.join(root_dir, _arg1)

        cmdline = '%s %s %s' % (op, opt, root_dir)
        execute_cmd(cmdline, False)
    elif op == 'mv':
        fdir =  root_dir
        arg1 = request.POST['arg1'].split(',')
        for _arg1 in arg1:
            fdir =os.path.join(fdir, _arg1)

        ddir =  root_dir
        arg2 = request.POST['arg2'].split(',')
        for _arg2 in arg2:
            ddir =os.path.join(ddir, _arg2)

        cmdline = '%s %s %s' % (op, fdir, ddir)
        execute_cmd(cmdline, False)

    ret={}
    ret['Result'] = 'OK'
    return HttpResponse(json.dumps(ret), content_type="application/json")

###################################################################################
# Form
###################################################################################
def generateAvailableResourceforCC(request, cc_name):
    rec = ecCCResources.objects.get(ccname=cc_name)
    emptyarray = []

    if request.POST['usage'] == 'lvd':
        rec.cc_usage = 'lvd'

    elif request.POST['usage'] == 'rvd':
        rec.cc_usage            = 'rvd'
        rec.network_mode        = request.POST['network_mode']

        rec.rdp_port_pool_def   = request.POST['rdp_port_def']

        portrange = rec.rdp_port_pool_def.split('-')
        portrange = range(int(portrange[0]), int(portrange[1]))

        rec.rdp_port_pool_list  = json.dumps(portrange)
        rec.used_rdp_ports      = json.dumps(emptyarray)

    elif request.POST['usage'] == 'vs':
        if request.POST['network_mode'] == 'flat':
            if request.POST['dhcp_type'] == 'external':
                rec.cc_usage            = 'vs'
                rec.network_mode        = 'flat'
                rec.dhcp_service        = 'external'

                rec.rdp_port_pool_def   = request.POST['rdp_port_def']
                portrange = rec.rdp_port_pool_def.split('-')
                portrange = range(int(portrange[0]), int(portrange[1]))

                rec.rdp_port_pool_list  = json.dumps(portrange)
                rec.used_rdp_ports      = json.dumps(emptyarray)

            if request.POST['dhcp_type'] == 'private':
                rec.cc_usage            = 'vs'
                rec.network_mode        = 'flat'
                rec.dhcp_service        = 'private'

                rec.rdp_port_pool_def   = request.POST['rdp_port_def']
                portrange = rec.rdp_port_pool_def.split('-')
                portrange = range(int(portrange[0]), int(portrange[1]))
                rec.rdp_port_pool_list  = json.dumps(portrange)
                rec.used_rdp_ports      = json.dumps(emptyarray)

                rec.dhcp_interface      = request.POST['dhcp_if']
                rec.dhcp_pool_def       = request.POST['dhcp_ip_def']


        if request.POST['network_mode'] == 'tree':
            if request.POST['dhcp_type'] == 'external':
                rec.cc_usage            = 'vs'
                rec.network_mode        = 'tree'
                rec.dhcp_service        = 'external'

                rec.rdp_port_pool_def   = request.POST['rdp_port_def']
                portrange = rec.rdp_port_pool_def.split('-')
                portrange = range(int(portrange[0]), int(portrange[1]))
                rec.rdp_port_pool_list  = json.dumps(portrange)
                rec.used_rdp_ports      = json.dumps(emptyarray)

                rec.pub_ip_pool_def       = request.POST['pub_ip_def']
                pubiprange                = rec.pub_ip_pool_def.split('-')
                pubiprange                = ipRange(pubiprange[0], pubiprange[1])
                rec.pub_ip_pool_list      = json.dumps(pubiprange)
                rec.used_pub_ip           = json.dumps(emptyarray)

            if request.POST['dhcp_type'] == 'private':
                rec.cc_usage            = 'vs'
                rec.network_mode        = 'tree'
                rec.dhcp_service        = 'private'

                rec.rdp_port_pool_def   = request.POST['rdp_port_def']
                portrange = rec.rdp_port_pool_def.split('-')
                portrange = range(int(portrange[0]), int(portrange[1]))
                rec.rdp_port_pool_list  = json.dumps(portrange)
                rec.used_rdp_ports      = json.dumps(emptyarray)

                rec.dhcp_interface      = request.POST['dhcp_if']
                rec.dhcp_pool_def       = request.POST['dhcp_ip_def']

                rec.pub_ip_pool_def       = request.POST['pub_ip_def']
                pubiprange                = rec.pub_ip_pool_def.split('-')
                pubiprange                = ipRange(pubiprange[0], pubiprange[1])
                rec.pub_ip_pool_list      = json.dumps(pubiprange)
                rec.used_pub_ip           = json.dumps(emptyarray)

    rec.save()

@login_required(login_url='/portal/admlogin')
def cc_modify_resources(request, cc_name):
    if request.method == 'POST':
        generateAvailableResourceforCC(request, cc_name)

        response = {}
        response['Result'] = 'OK'

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        rec = ecCCResources.objects.get(ccname=cc_name)
        context = {
            'pagetitle' : _("Configure CC Network Resources"),
            'ccres' : rec,
        }

        return render(request, 'clc/form/cc_modify_resource.html', context)

###############################################ti##################################
# create a new images & modify existing image
###################################################################################

# {
#     # 1. general
#     'ostype'            :
#     'usage'             :
#
#     # 2. hardware
#     'memeory'           :
#     'cpus'              :
#     'disk_type'         :
#     'audio_para'        :
#
#     # 3. network
#     3.1 'rdp_port'          :
#     3.2 'netwowrkcards'     :  VM's network card property, ip/mac from table ecDHCPEthers
#     [
#         { 'nic_type': "", 'nic_mac': "" , 'nic_ip': ""},
#         { 'nic_type': "", 'nic_mac': "" , 'nic_ip': ""},
#         { 'nic_type': "", 'nic_mac': "" , 'nic_ip': ""},
#         ... ...
#     ]
#     3.3.1 'disks' : [
#         {
#           'file'      :  '/storage/images/imgid/machine'
#           'mtype'     :  'normal'
#         }
#         {
#           'file'      :  '/storage/space/database/images/imgid/database'
#           'mtype'     :  'write-through'
#         }
#     ]
#     3.3.2 'folders'   : [
#         '/storage/space/software/',
#         '/storage/space/prv-data/<user>/',
#         '/storage/space/pub-data/'
#     ]
#     3.4 pub_ip, prv_ip, iptable
#     'rdp_ip'          :   used for vm management
#     'web_ip'          :   used for accessing vm web server
#
#     'iptable_rules'     :
#     [
#         'rule1',
#         'rule2',
#         ... ...
#     ]
#     3.5
#     'web_accessURL'     :  web_ip:80, or ex_ccip:xxxx
#     'mgr_accessURL'     :  rdp_ip:rdp_port, or ex_ccip:rdp_port

#     # 4. related to issuer
#     'run_with_snapshot' : 1, 0
#     'pds' : 20G # 0 means no pds
#     'sds' : yes or no  # means shared data storage
#     'poweroff_mode' : auto | manual,
#     'poweroff_time' : 1h, 1d, 1w # valid only if power_mode is auto
# }


def releaseRuntimeOptionForImageBuild(_tid, _runtime_option=None):
    logger.error(' --- releaseRuntimeOptionForImageBuild ... ...')
    tidrec = ectaskTransaction.objects.get(tid=_tid)
    creator = tidrec.user

    if _runtime_option == None:
        if len(tidrec.runtime_option) > 0:
            runtime_option = json.loads(tidrec.runtime_option)
        else:
            return
    else:
        runtime_option = _runtime_option

    ccobj       = ecServers.objects.get(ip0=tidrec.ccip, role='cc')
    ccres_info  = ecCCResources.objects.get(ccmac0=ccobj.mac0)

    # release CC Resource
    # 1. rdp port
    if 'rdp_port' in runtime_option.keys() and runtime_option['rdp_port']  != '':
        logger.error('release rdp port %s' % runtime_option['rdp_port'])
        available_rdp_port = json.loads(ccres_info.rdp_port_pool_list)
        used_rdp_ports     = json.loads(ccres_info.used_rdp_ports)

        available_rdp_port, used_rdp_ports = free_rdp_port(available_rdp_port, used_rdp_ports, runtime_option['rdp_port'])

        ccres_info.rdp_port_pool_list   = json.dumps(available_rdp_port)
        ccres_info.used_rdp_ports       = json.dumps(used_rdp_ports)

        ccres_info.save()

    # 2. release web_ip
    if 'web_ip' in runtime_option.keys() and \
        runtime_option['web_ip'] != ''   and \
        runtime_option['networkcards'] == 'tree' and \
        ccres_info.cc_usage == 'vs' :
        logger.error('release web ip %s' % runtime_option['web_ip'])
        availabe_web_ips = json.loads(ccres_info.pub_ip_pool_list)
        used_web_ips     = json.loads(ccres_info.used_pub_ip)

        availabe_web_ips, userd_web_ips = free_web_ip(availabe_web_ips, used_web_ips)

        ccres_info.pub_ip_pool_list = json.dumps(availabe_web_ips)
        ccres_info.used_pub_ip      = json.dumps(used_web_ips)

        ccres_info.save()

    # 3. release ether if it is VS and
    if ccres_info.cc_usage == 'vs' and runtime_option['usage'] == 'server':
        ethers_free(tidrec.insid)

    # 3. release iptables
    if 'iptable_rules' in runtime_option.keys() and runtime_option['iptable_rules'] != []:
        logger.error('--- notify cc %s to release iptables ... ...' % tidrec.ccip)
        if DAEMON_DEBUG == True:
            url = 'http://%s:8000/cc/api/1.0/image/create/task/removeIPtables' % tidrec.ccip
        else:
            url = 'http://%s/cc/api/1.0/image/create/task/removeIPtables' % tidrec.ccip

        payload = {
            'iptable_rules' : runtime_option['iptable_rules']
        }
        r = requests.post(url, data=payload)
        logger.error("--- --- --- " + url + ":" + r.content)

def genVMDisks(tid, usage):
    tid_info = tid.split(':')
    src_imgid = tid_info[0]
    dst_imgid = tid_info[1]
    ins_id    = tid_info[2]

    disks = []
    c = {}
    d = {}
    e = {}
    if ins_id.find('TMP') == 0:
        # add disk c
        if src_imgid == dst_imgid:
            c['file'] = '/storage/images/%s/machine' % dst_imgid
        else:
            c['file'] = '/storage/tmp/images/%s/machine' % dst_imgid
        c['mtype']   = 'normal'
        disks.append(c)

        if usage == 'server':
            d['file']    = '/storage/space/database/images/%s/database' % dst_imgid
            d['mtype']   = 'normal'
            disks.append(d)

        e['file']    = '/storage/images/data'
        e['mtype']   = 'multiattach'
        disks.append(e)

    if ins_id.find('VD') == 0 or ins_id.find('TVD') == 0 :
        c['file']    = '/storage/images/%s/machine' % dst_imgid
        c['mtype']   = 'multiattach'
        disks.append(c)

    if ins_id.find('VS') == 0:
        c['file']    = '/storage/images/%s/machine' % dst_imgid
        c['mtype']   = 'multiattach'
        disks.append(c)

        d['file']    = '/storage/space/database/instances/%s/database' % ins_id
        d['mtype']   = 'writethrough'
        disks.append(d)

    return disks

def genVMFolders(tid, usage):
    tid_info = tid.split(':')
    src_imgid = tid_info[0]
    dst_imgid = tid_info[1]
    ins_id    = tid_info[2]

    folders = []

    if ins_id.find('TMP') == 0:
        f = {
            'path': '/storage/space/software',
            'name': 'software',
        }
        folders.append(f)

    if ins_id.find('VD') == 0 or ins_id.find('TVD') == 0 :
        trec = ectaskTransaction.objects.get(tid=tid)
        f1 = {
            'path': '/storage/space/prv-data/%s' % trec.user,
            'name': 'prvdata',
        }
        f2 = {
            'path': '/storage/space/pub-data',
            'name': 'pubdata',
        }
        folders.append(f1)
        folders.append(f2)

    if ins_id.find('VS') == 0:
        # folders.append('/storage/space/software')
        pass

    return folders

def genRuntimeOptionForImageBuild(transid):
    logger.error("--- --- --- genRuntimeOptionForImageBuild")
    tid_info = transid.split(':')
    src_imgid = tid_info[0]
    dst_imgid = tid_info[1]
    ins_id    = tid_info[2]

    tid_rec = ectaskTransaction.objects.get(tid=transid)

    ccip = tid_rec.ccip
    ncip = tid_rec.ncip

    ccobj       = ecServers.objects.get(ip0=ccip, role='cc')
    ccres_info  = ecCCResources.objects.get(ccmac0=ccobj.mac0)
    ncobj       = ecServers.objects.get(ip0=ncip, role='nc')

    runtime_option = {}

    # 1. general option
    img_info                        = ecImages.objects.get(ecid = src_imgid)
    runtime_option['ostype']        = img_info.ostype
    runtime_option['usage']         = img_info.img_usage

    if ins_id.find('TMP') == 0 or ins_id.find('TVD') == 0 :
        if img_info.img_usage == "desktop":
            vmtype = 'vdsmall'
        else:
            vmtype = 'vssmall'

        # 2. hardware option
        vmtype_info                     = ecVMTypes.objects.get(name=vmtype)
        runtime_option['memory']        = vmtype_info.memory
        runtime_option['cpus']          = vmtype_info.cpus
    else:
        if ins_id.find('VS') == 0:
            insobj = ecVSS.objects.get(insid=ins_id)
        if ins_id.find('VD') == 0:
            insobj = ecVDS.objects.get(insid=ins_id)
        runtime_option['memory']    = insobj.memory
        runtime_option['cpus']      = insobj.cpus
    logger.error('allocate memory  %sG for %s' % (runtime_option['memory'], transid))

    ostype_info                     = ecOSTypes.objects.get(ec_ostype = img_info.ostype)
    runtime_option['disk_type']     = ostype_info.ec_disk_type
    runtime_option['audio_para']    = ostype_info.ec_audio_para

    # 3 network option

    networkMode = ccres_info.network_mode

    # 3.1 allocate rpd port
    available_rdp_port = json.loads(ccres_info.rdp_port_pool_list)
    used_rdp_ports     = json.loads(ccres_info.used_rdp_ports)

    available_rdp_port, used_rdp_ports, newport = allocate_rdp_port(available_rdp_port, used_rdp_ports)
    if newport == None:
        runtime_option['rdp_port']  = ''
        return None, _('Need more rdp port resources!.')
    else:
        runtime_option['rdp_port']                  = newport
        logger.error('allocate rdp port %s for %s' % (newport, transid))

    ccres_info.rdp_port_pool_list   = json.dumps(available_rdp_port)
    ccres_info.used_rdp_ports       = json.dumps(used_rdp_ports)

    # 3.2 set netcard in vm
    networkcards = []
    netcard = {}
    netcard['nic_type'] = ostype_info.ec_nic_type
    if ccres_info.cc_usage == 'rvd' or runtime_option['usage'] == 'desktop':
        netcard['nic_mac']  = ''
        netcard['nic_ip']   = ''
    if ccres_info.cc_usage == 'vs' and runtime_option['usage'] == 'server':
        netcard['nic_mac'], netcard['nic_ip'], web_port = ethers_allocate(ccres_info.ccname, ins_id)
        if netcard['nic_mac'] == None:
            releaseRuntimeOptionForImageBuild(transid, runtime_option)
            return None, _('Need more ether resources.')
        else:
            runtime_option['web_ip'] = netcard['nic_ip']
            runtime_option['web_port'] = web_port
            logger.error('allocate web port %s for %s' % (web_port, transid))

    networkcards.append(netcard)
    runtime_option['networkcards'] = networkcards

    # 3.3 add disks and folders
    runtime_option['disks']     = genVMDisks(transid,   runtime_option['usage'])
    runtime_option['folders']   = genVMFolders(transid, runtime_option['usage'])

    # 3.4 set public ip and private ip and iptable
    iptables = []

    if networkMode == 'flat':
        runtime_option['ex_ip']   = ncobj.eip
        runtime_option['rdp_ip']  = ncip
    if networkMode == 'tree':
        # proxy by cc
        runtime_option['ex_ip']   = ccobj.eip
        runtime_option['rdp_ip']  = ccip

        # set iptable rule for rdp access
        ipt = {
            'src_ip': ccip,
            'dst_ip': ncip,
            'src_port': newport,
            'dst_port': newport,
            'ins_id'  : ins_id,
        }
        iptables.append(ipt)

        # set iptable rule for web service
        if ccres_info.cc_usage == 'vs':
            # allocate web ip
            availabe_web_ips = json.loads(ccres_info.pub_ip_pool_list)
            used_web_ips     = json.loads(ccres_info.used_pub_ip)

            availabe_web_ips, userd_web_ips, new_web_ip = allocate_web_ip(availabe_web_ips, used_web_ips)
            if new_web_ip == None:
                runtime_option['web_ip'] = ''
                releaseRuntimeOptionForImageBuild(transid, runtime_option)
                return None, _('Need more Proxy Web IP resources for Cluster.')
            else:
                runtime_option['web_ip'] = new_web_ip

                ccres_info.pub_ip_pool_list = json.dumps(availabe_web_ips)
                ccres_info.used_pub_ip      = json.dumps(used_web_ips)

                ipt['src_ip'] = runtime_option['web_ip']
                ipt['dst_ip'] = netcard['nic_ip']
                ipt['src_port'] = 0  # port 0 means all port
                ipt['dst_port'] = 0
                iptables.append(ipt)

    runtime_option['iptable_rules'] = iptables

    # 3.4 set web_accessURL and mgr_accessURL
    runtime_option['web_accessURL']     = ''
    runtime_option['ex_web_accessURL']  = ''
    if ccres_info.cc_usage == 'rvd' or runtime_option['usage'] == 'desktop':
        runtime_option['mgr_accessURL']     = "%s:%s" % (runtime_option['rdp_ip'], runtime_option['rdp_port'])
        runtime_option['ex_mgr_accessURL']  = "%s:%s" % (runtime_option['ex_ip'],  runtime_option['rdp_port'])
    if ccres_info.cc_usage == 'vs' and runtime_option['usage'] == 'server':
        runtime_option['web_accessURL']     = 'http://%s' % runtime_option['web_ip']
        runtime_option['ex_web_accessURL']  = 'http://%s:%s' % (runtime_option['ex_ip'], runtime_option['web_port'])
        runtime_option['mgr_accessURL']     = "%s:%s" % (runtime_option['rdp_ip'], runtime_option['rdp_port'])
        runtime_option['ex_mgr_accessURL']  = "%s:%s" % (runtime_option['ex_ip'],  runtime_option['rdp_port'])

    # issuer's property
    runtime_option['run_with_snapshot'] = 1

    ccres_info.save()
    return runtime_option, ''

def genIPTablesRule(fromip, toip, port):
    return {}

def getValidMgrURL(request, runtime_option):
    if request.META['REMOTE_ADDR'] == '10.181.4.103':
        mgr_url = runtime_option['ex_mgr_accessURL']
    else:
        srciptype = getIPType(request.META['REMOTE_ADDR'])
        if srciptype == 'PUBLIC':
            mgr_url = runtime_option['ex_mgr_accessURL']
        else:
            mgr_url = runtime_option['mgr_accessURL']

    return mgr_url

def getValidWebURL(request, runtime_option):
    if request.META['REMOTE_ADDR'] == '10.181.4.103':
        web_url = runtime_option['ex_web_accessURL']
    else:
        srciptype = getIPType(request.META['REMOTE_ADDR'])
        if srciptype == 'PUBLIC':
            web_url = runtime_option['ex_web_accessURL']
        else:
            web_url = runtime_option['web_accessURL']

    return web_url

def vm_display(request, srcid, dstid, insid):
    _tid = '%s:%s:%s' % (srcid, dstid, insid)
    try:
        rec = ectaskTransaction.objects.get(tid=_tid)
        runtime_option = json.loads(rec.runtime_option)

        mgr_url = getValidMgrURL(request, runtime_option)

        context = {
            'pagetitle'     : _('cloud desktop'),
            'url'           : mgr_url,
        }
        return render(request, 'clc/rdpclient/vm_display.html', context)
    except Exception as e:
        logger.error('vm_display error: tid=%s, error=%s' % (_tid, str(e)))
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : str(e),
            'suggestion'    : 'check your CC configuration and release some running VMs '
        }
        return render(request, 'clc/error.html', context)

def vm_run(request, insid):
    if insid.find('VD') == 0:
        vmrec = ecVDS.objects.get(insid=insid)
    elif insid.find('VS') == 0:
        vmrec = ecVSS.objects.get(insid=insid)

    _tid  = '%s:%s:%s' % (vmrec.imageid, vmrec.imageid, insid)

    # if tid exist, just call view
    # else find resource and create tid
    trecs = ectaskTransaction.objects.filter(tid=_tid)
    if trecs.count() > 0:
        return image_create_task_view(request, vmrec.imageid, vmrec.imageid, insid)
    else:
        _ccip, _ncip, _msg = findVMRunningResource(request, insid)
        if _ncip == None:
            # not find proper cc,nc for build image
            context = {
                'pagetitle'     : _('Error Report'),
                'error'         : _msg,
            }
            return render(request, 'clc/error.html', context)
        else:
            rec = ectaskTransaction(
                 tid         = _tid,
                 srcimgid    = vmrec.imageid,
                 dstimgid    = vmrec.imageid,
                 insid       = insid,
                 user        = request.user.username,
                 phase       = 'preparing',
                 state       = "init",
                 progress    = 0,
                 ccip        = _ccip,
                 ncip        = _ncip,
            )
            rec.save()
            runtime_option, error = genRuntimeOptionForImageBuild(_tid)
            if runtime_option == None:
                rec.delete()
                context = {
                    'pagetitle'     : _('Error Report'),
                    'error'         : error,
                }
                return render(request, 'clc/error.html', context)
            else:
                rec.runtime_option = json.dumps(runtime_option)
                rec.save()

            return image_create_task_view(request, vmrec.imageid, vmrec.imageid, insid)

def image_create_task_start(request, srcid):
    logger.error("--- --- --- start_image_create_task")
    #############
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    objs = ecImages_auth.objects.filter(ecid=srcid, role_value=ua_role_value.ec_authpath_value )
    if objs[0].create != True:
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _('current user not allowed to create new images'),
            'suggestion'    : _('Ask eduCloud.admin to assign CREATE rigth.'),
        }
        return render(request, 'clc/error.html', context)

    # create ectaskTransation Record
    _srcimgid        = srcid
    _dstimageid      = 'IMG' + genHexRandom()
    _instanceid      = 'TMP' + genHexRandom()
    _tid             = '%s:%s:%s' % (_srcimgid, _dstimageid, _instanceid )

    logger.error("tid=%s" % _tid)

    _ccip, _ncip, _msg = findBuildResource(srcid)

    if _ncip == None:
        # not find proper cc,nc for build image
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _msg,
        }
        return render(request, 'clc/error.html', context)
    else:
        rec = ectaskTransaction(
             tid         = _tid,
             srcimgid    = _srcimgid,
             dstimgid    = _dstimageid,
             insid       = _instanceid,
             user        = request.user.username,
             phase       = 'preparing',
             state       = "init",
             progress    = 0,
             ccip        = _ccip,
             ncip        = _ncip,
        )
        rec.save()

        runtime_option, error = genRuntimeOptionForImageBuild(_tid)
        if runtime_option == None:
                rec.delete()
                context = {
                    'pagetitle'     : _('Error Report'),
                    'error'         : error,
                }
                return render(request, 'clc/error.html', context)
        else:
            rec.runtime_option = json.dumps(runtime_option)
            rec.save()

        return image_create_task_view(request, _srcimgid,_dstimageid, _instanceid)


def getVM_ManagedURL(request, taskid):
    rec = ectaskTransaction.objects.get(tid=taskid)
    runtime_option = json.loads(rec.runtime_option)
    mgr_url = getValidMgrURL(request, runtime_option)

    return mgr_url

def getVM_WebURL(request, taskid):
    rec = ectaskTransaction.objects.get(tid=taskid)
    runtime_option = json.loads(rec.runtime_option)
    web_url = getValidWebURL(request, runtime_option)

    return web_url

def image_create_task_prepare(request, srcid, dstid, insid):
    logger.error("--- --- --- prepare_image_create_task")

    _tid = "%s:%s:%s" % (srcid, dstid, insid)

    rec = ectaskTransaction.objects.get(tid=_tid)
    rec.phase = "preparing"
    rec.state = "downloading"
    rec.progress = 0
    rec.save()

    # # send request to CC to work
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/cc/api/1.0/image/create/task/prepare' % rec.ccip
    else:
        url = 'http://%s/cc/api/1.0/image/create/task/prepare' % rec.ccip

    payload = {
        'tid'  :            _tid,
        'ncip' :            rec.ncip,
        'runtime_option' :  rec.runtime_option,
    }
    r = requests.post(url, data=payload)
    logger.error("--- --- --- " + url + ":" + r.content)

    return HttpResponse(r.content, content_type="application/json")

def image_create_task_prepare_success(request, srcid, dstid, insid):
    logger.error("--- --- --- image_create_task_prepare_success")

    try:
        _tid = "%s:%s:%s" % (srcid, dstid, insid)

        rec = ectaskTransaction.objects.get(tid=_tid)
        rec.phase = "preparing"
        rec.state = 'done'
        rec.progress = 0
        rec.save()
    except Exception as e:
        logger.error('--- image_create_task_prepare_success error = %s ' % str(e))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def image_create_task_prepare_failure(request, srcid, dstid, insid):
    logger.error("--- --- --- image_create_task_prepare_failure")

    try:
        _tid = "%s:%s:%s" % (srcid, dstid, insid)

        rec = ectaskTransaction.objects.get(tid=_tid)
        rec.phase = "preparing"
        rec.state = 'init'
        rec.progress = 0
        rec.save()
    except Exception as e:
        logger.error('--- image_create_task_prepare_failure error = %s ' % str(e))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def image_create_task_run(request, srcid, dstid, insid):
    logger.error("--- --- --- run_image_create_task")

    try:
        _tid = "%s:%s:%s" % (srcid, dstid, insid)

        rec = ectaskTransaction.objects.get(tid=_tid)
        rec.phase = "editing"
        rec.state = 'booting'
        rec.progress = 0
        rec.save()

        # now everything is ready, start to run instance
        if DAEMON_DEBUG == True:
            url = 'http://%s:8000/cc/api/1.0/image/create/task/run' % rec.ccip
        else:
            url = 'http://%s/cc/api/1.0/image/create/task/run' % rec.ccip
        payload = {
            'tid'  :            _tid,
            'ncip' :            rec.ncip,
            'runtime_option' :  rec.runtime_option,
        }
        r = requests.post(url, data=payload)
        logger.error("--- --- --- " + url + ":" + r.content)

    except Exception as e:
        logger.error('--- image_create_task_stop error = %s ' % str(e))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def image_create_task_stop(request, srcid, dstid, insid):
    logger.error("--- --- --- stop_image_create_task")

    try:
        _tid = "%s:%s:%s" % (srcid, dstid, insid)
        rec = ectaskTransaction.objects.get(tid=_tid)
        rec.phase = "editing"
        rec.state = 'stopped'
        rec.progress = 0
        rec.save()

        if DAEMON_DEBUG == True:
            url = 'http://%s:8000/cc/api/1.0/image/create/task/stop' % rec.ccip
        else:
            url = 'http://%s/cc/api/1.0/image/create/task/stop' % rec.ccip

        payload = {
            'tid'  :            _tid,
            'ncip' :            rec.ncip,
            'runtime_option' :  rec.runtime_option,
        }

        r = requests.post(url, data=payload)
        logger.error("--- --- --- " + url + ":" + r.content)
    except Exception as e:
        logger.error('--- image_create_task_stop error = %s ' % str(e))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def image_create_task_updatevmstatus(request, srcid, dstid, insid, vmstatus):
    logger.error("--- --- --- image_create_task_updatevmstatus")

    try:
        _tid = "%s:%s:%s" % (srcid, dstid, insid)
        rec = ectaskTransaction.objects.get(tid=_tid)
        rec.state = vmstatus
        rec.save()
    except Exception as e:
        logger.error('--- image_create_task_stop error = %s ' % str(e))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def image_create_task_getvmstatus(request, srcid, dstid, insid):
    # logger.error("--- --- --- image_create_task_getvmstatus")

    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    _tid = "%s:%s:%s" % (srcid, dstid, insid)

    payload = {
        'type' : 'taskstatus',
        'phase': "editing",
        'state': 'booting',
        'tid': _tid,
        'failed' : 0
    }

    try:
        tidrec = ectaskTransaction.objects.get(tid=_tid)
        ncobj = ecServers.objects.get(ip0=tidrec.ncip, role='nc')
        key = str("nc#" + ncobj.mac0 + "#status")
        nc_info = mc.get(key)
        nc_info = json.loads(nc_info)

        if 'vm_data' in nc_info.keys():
            vminfo = nc_info['vm_data']
            for vm in vminfo:
                if vm['insid'] == insid:
                    payload['state'] = vm['state']
                    break
    except Exception as e:
        logger.error("image_create_task_getvmstatus Exception : %s" % str(e))
        payload['state'] = 'stopped'

    response = json.dumps(payload)
    logger.error('image_create_task_getvmstatus = %s : %s' % (_tid, response))
    return HttpResponse(response, content_type="application/json")

def image_create_task_getprogress(request, srcid, dstid, insid):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    tid = "%s:%s:%s" % (srcid, dstid, insid)
    try:
        payload = mc.get(str(tid))
        if payload == None:
            payload = {
                'type': 'taskstatus',
                'phase': "preparing",
                'state': 'downloading',
                'progress': 0,
                'tid': tid,
                'prompt': '',
                'errormsg': '',
                'failed' : 0
            }
            response = json.dumps(payload)
        else:
            response = payload
            payload = json.loads(payload)
            # logger.error("lkf: get progress = %s", payload['progress'])
            if payload['failed'] == 1:
                mc.delete(str(tid))
    except Exception as e:
        payload = {
            'type': 'taskstatus',
            'phase': "preparing",
            'state': 'downloading',
            'progress': 0,
            'tid': tid,
            'prompt': '',
            'errormsg': '',
            'failed' : 0
        }
        response = json.dumps(payload)

    return HttpResponse(response, content_type="application/json")

def image_create_task_submit(request, srcid, dstid, insid):
    logger.error("--- --- --- submit_image_create_task")

    _tid = "%s:%s:%s" % (srcid, dstid, insid)
    rec = ectaskTransaction.objects.get(tid=_tid)
    rec.phase = "submitting"
    rec.state = 'uploading'
    rec.progress = 0
    rec.save()

    # # send request to CC to work
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/cc/api/1.0/image/create/task/submit' % rec.ccip
    else:
        url = 'http://%s/cc/api/1.0/image/create/task/submit' % rec.ccip

    payload = {
        'tid'  :            _tid,
        'ncip' :            rec.ncip,
        'runtime_option' :  rec.runtime_option,
    }

    r = requests.post(url, data=payload)
    logger.error("--- --- --- " + url + ":" + r.content)

    return HttpResponse(r.content, content_type="application/json")

def image_create_task_getsubmitprogress(request, srcid, dstid, insid):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    tid = "%s:%s:%s" % (srcid, dstid, insid)
    try:
        payload = mc.get(str(tid))
        if payload == None:
            payload = {
                'type': 'taskstatus',
                'phase': "submitting",
                'state': 'uploading',
                'progress': 0,
                'tid': tid,
                'prompt': '',
                'errormsg': '',
                'failed' : 0
            }
            response = json.dumps(payload)
        else:
            response = payload
            payload = json.loads(payload)
            if payload['failed'] == 1:
                mc.delete(str(tid))
    except Exception as e:
        payload = {
            'type': 'taskstatus',
            'phase': "submitting",
            'state': 'uploading',
            'progress': 0,
            'tid': tid,
            'prompt': '',
            'errormsg': '',
            'failed' : 0
        }
        response = json.dumps(payload)

    # logger.error("lkf: get progress = %s", response)
    return HttpResponse(response, content_type="application/json")

def image_modify_task_start(request, srcid):
    #############
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    objs = ecImages_auth.objects.filter(ecid=srcid, role_value=ua_role_value.ec_authpath_value )
    if objs[0].create != True:
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _('current user not allowed to modify images'),
            'suggestion'    : _('Ask eduCloud.admin to assign WRITE rigth.'),
        }
        return render(request, 'clc/error.html', context)


    # create ectaskTransation Record
    _srcimgid        = srcid
    _dstimageid      = srcid
    _instanceid      = 'TMP' + genHexRandom()
    _tid             = '%s:%s:%s' % (_srcimgid, _dstimageid, _instanceid )

    logger.error("tid=%s" % _tid)

    _ccip, _ncip, _msg = findBuildResource(srcid)

    if _ncip == None:
        # not find proper cc,nc for build image
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _msg,
        }
        return render(request, 'clc/error.html', context)
    else:
        rec = ectaskTransaction(
             tid         = _tid,
             srcimgid    = _srcimgid,
             dstimgid    = _dstimageid,
             insid       = _instanceid,
             user        = request.user.username,
             phase       = 'preparing',
             state       = "init",
             progress    = 0,
             ccip        = _ccip,
             ncip        = _ncip,
        )
        rec.save()
        runtime_option, error = genRuntimeOptionForImageBuild(_tid)
        if runtime_option == None:
                rec.delete()
                context = {
                    'pagetitle'     : _('Error Report'),
                    'error'         : error,
                }
                return render(request, 'clc/error.html', context)
        else:
            rec.runtime_option = json.dumps(runtime_option)
            rec.save()

        return image_create_task_view(request, _srcimgid,_dstimageid, _instanceid)

def image_create_task_view(request,  srcid, dstid, insid):
    _tid = "%s:%s:%s" % (srcid, dstid, insid)

    rec = ectaskTransaction.objects.get(tid=_tid)
    imgobj = ecImages.objects.get(ecid = srcid)
    managed_url = getVM_ManagedURL(request, _tid)
    if insid.find('TMP') == 0:
        submit = 1
    else:
        submit = 0

    context = {
        'pagetitle' : _("image build"),
        'task'      : rec,
        'rdp_url'   : managed_url,
        'imgobj'    : imgobj,
        'submit'    : submit,
    }

    return render(request, 'clc/wizard/image_create_wizard.html', context)

def image_create_task_submit_failure(request,  srcid, dstid, insid):
    logger.error("--- --- --- image_create_task_submit_failure")

    try:
        _tid = "%s:%s:%s" % (srcid, dstid, insid)
        rec = ectaskTransaction.objects.get(tid=_tid)

        rec.phase = "submitting"
        rec.statue = 'init'
        rec.progress = 0
        rec.save()

    except Exception as e:
        logger.error('--- image_create_task_stop error = %s ' % str(e))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def image_create_task_submit_success(request, srcid, dstid, insid):
    logger.error("--- --- --- image_create_task_submit_success")
    _tid = "%s:%s:%s" % (srcid, dstid, insid)

    try:
        trec = ectaskTransaction.objects.get(tid=_tid)
        trec.phase = "submitting"
        trec.state = 'done'
        # trec.completed = True
        trec.progress = 0
        trec.save()

        imgfile_path = '/storage/images/' + dstid + "/machine"
        imgfile_size = os.path.getsize(imgfile_path) / (1024.0 * 1024 * 1024)
        imgfile_size = round(imgfile_size, 2)

        # 4 update database
        if srcid != dstid:
            srcimgrec = ecImages.objects.get(ecid=srcid)

            dstimgrec = ecImages(
                ecid    = dstid,
                name    = dstid,
                ostype  = srcimgrec.ostype,
                img_usage   = srcimgrec.img_usage,
                version = "1.0.0",
                size    = imgfile_size,
            )
            dstimgrec.save()
            logger.error('create new image record: %s %s %s' % (dstid, srcimgrec.ostype, srcimgrec.img_usage))

            rec = ecImages_auth(
                ecid = dstid,
                role_value = 'eduCloud.admin',
                read = True,
                write = True,
                execute = True,
                create = True,
                delete = True,
            )
            rec.save()

            rec = ecAccount.objects.get(userid=trec.user)
            auth_name = rec.ec_authpath_name
            rec = ecAuthPath.objects.get(ec_authpath_name = auth_name)
            if rec.ec_authpath_value != 'eduCloud.admin':
                newrec = ecImages_auth(
                    ecid = dstid,
                    role_value = rec.ec_authpath_value,
                    read = True,
                    write = True,
                    execute = True,
                    create = True,
                    delete = False,
                )
                newrec.save()

            WriteImageVersionFile(dstid, '1.0.0')
            logger.error("--- --- --- create a new image record successfully")
        else:
            oldversionNo = ReadImageVersionFile(dstid)
            newversionNo = IncreaseImageVersion(oldversionNo)
            WriteImageVersionFile(dstid, newversionNo)

            dstimgrec = ecImages.objects.get(ecid=dstid)
            dstimgrec.version = newversionNo
            dstimgrec.size    = imgfile_size
            dstimgrec.save()
            logger.error("--- --- --- update image record successfully")

    except Exception as e:
        logger.error('--- image_create_task_submit_success error = %s ' % str(e))

    # clear transaction record
    delet_task_by_id(_tid)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def getCCObjListbyRequestUser(request, ccs):
    #############
    ua              = ecAccount.objects.get(userid=request.user)
    ua_role_value   = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    role_prefix     = ua_role_value.ec_authpath_value.split('.admin')[0]

    ccobj_list = []
    for cc in ccs:
        sobjs = ecServers_auth.objects.filter(srole='cc', mac0=cc.ccmac0, role_value__contains=role_prefix)
        if sobjs.count() == 0:
            continue
        ccobj_list.append(cc)

    return ccobj_list


def image_add_vm(request, imgid):
    #############
    ua              = ecAccount.objects.get(userid=request.user)
    ua_role_value   = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    objs            = ecImages_auth.objects.filter(ecid=imgid, role_value=ua_role_value.ec_authpath_value )
    
    if objs[0].create != True:
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _('current user not allowed to create new VM'),
            'suggestion'    : _('Ask eduCloud.admin to assign CREATE rigth.'),
        }
        return render(request, 'clc/error.html', context)

    imgobj = ecImages.objects.get(ecid = imgid)

    if imgobj.img_usage == 'desktop':
        _instanceid      = 'VD' + genHexRandom()
        if is_vd_allowed_in_vscc() == True:
            ccs  = ecCCResources.objects.filter()
        else:
            ccs  = ecCCResources.objects.filter(cc_usage='vd')
    if imgobj.img_usage == 'server':
        _instanceid      = 'VS' + genHexRandom()
        ccs  = ecCCResources.objects.filter(cc_usage='vs')

    ccs = getCCObjListbyRequestUser(request, ccs)

    if ccs == []:
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _('current user not allowed to manage any cluster'),
            'suggestion'    : _('Ask eduCloud.admin to assign a cluster to current user.'),
        }
        return render(request, 'clc/error.html', context)
    else:
        context = {
                'pagetitle' : _("VM Create"),
                'imgobj'    : imgobj,
                'insid'     : _instanceid,
                'ccs'       : ccs,
                'vm'        : None,
        }

        return render(request, 'clc/wizard/vs_create_wizard.html', context)

def image_edit_vm(request, imgid, insid):

    imgobj = ecImages.objects.get(ecid = imgid)

    ccs  = ecServers.objects.filter(role='cc')
    vm   = ecVSS.objects.get(insid=insid)
    context = {
            'pagetitle' : _("VM Create"),
            'imgobj'    : imgobj,
            'insid'     : insid,
            'ccs'       : ccs,
            'vm'        : vm,
    }

    return render(request, 'clc/wizard/vs_create_wizard.html', context)

#################################################################################
# jTable views
#################################################################################
@login_required(login_url='/portal/admlogin')
def jtable_images(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/images_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_tasks(request):
    return render(request, 'clc/jtable/tasks_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_vss(request):
    return render(request, 'clc/jtable/vss_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_vds(request):
    return render(request, 'clc/jtable/vds_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_settings_for_authapth(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/authpath_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_settings_for_ostypes(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/ostypes_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_settings_for_rbac(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/rbac_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_settings_for_vmusage(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/vmusage_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_settings_for_serverrole(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/serverrole_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_settings_for_vmtypes(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/vmtypes_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_settings_for_hypervisor(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'clc/jtable/hypervisor_table.html', context)

@login_required(login_url='/portal/admlogin')
def jtable_servers_cc(request):

    return render(request, 'clc/jtable/servers_cc_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_servers_nc(request):
    return render(request, 'clc/jtable/servers_nc_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_servers_lnc(request):
    return render(request, 'clc/jtable/servers_lnc_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_terminal(request):
    return render(request, 'clc/jtable/servers_tnc_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_active_accounts(request):
    return render(request, 'clc/jtable/active_account_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_inactive_accounts(request):
    return render(request, 'clc/jtable/inactive_account_table.html', {})

@login_required(login_url='/portal/admlogin')
def jtable_ethers(request, cc_name):
    context = {
        'ccname' : cc_name
    }
    return render(request, 'clc/jtable/ethers_table.html', context)

def ethers_allocate(ccname, _insid):
    if _insid.find('VS') == 0:
        try:
            vssobj = ecVSS.objects.get(insid = _insid)
            e = ecDHCPEthers.objects.get(mac=vssobj.mac, ccname=ccname)
            e.insid = _insid
            e.save()
            logger.error("allocate VS ether %s-%s-%s" % (e.mac, e.ip, e.ex_web_proxy_port))
            return e.mac, e.ip, e.ex_web_proxy_port
        except:
            return None, None, None
    else:
        es = ecDHCPEthers.objects.filter(insid='', ccname=ccname)
        if es.count() > 0:
            e = ecDHCPEthers.objects.get(mac=es[0].mac)
            e.insid = _insid
            e.save()
            logger.error("allocate TMP ether %s-%s-%s" % (e.mac, e.ip, e.ex_web_proxy_port))
            return e.mac, e.ip, e.ex_web_proxy_port
        else:
            return None, None, None

def ethers_free(insid):
    ecs = ecDHCPEthers.objects.filter(insid=insid)
    if ecs.count() > 0:
        e = ecDHCPEthers.objects.get(insid=insid)
        e.insid = ''
        e.save()
        logger.error('release ethers %s %s %s %s' % (e.mac, e.ip, e.ex_web_proxy_port, insid))
    else:
        logger.error('no ethers allocated to %s' % insid)


#################################################################################
# API Version 1.0 for accessing data model by POST request
#################################################################################

# settings tables ecAuthPath
# -----------------------------------
def list_authpath(request):
    response = {}
    data = []

    recs = ecAuthPath.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['ec_authpath_value'] = rec.ec_authpath_value
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def authpath_optionlist(request):
    response = {}
    data = []

    recs = ecAuthPath.objects.all()
    for rec in recs:
        jrec = {}
        jrec['DisplayText'] = rec.ec_authpath_name
        jrec['Value'] = rec.ec_authpath_name
        data.append(jrec)

    response['Options'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_authpath(request):
    response = {}

    rec = ecAuthPath.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_authpath(request):
    response = {}

    rec = ecAuthPath.objects.get(id=request.POST['id']);
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.ec_authpath_value = request.POST['ec_authpath_value']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_authpath(request):
    response = {}
    data = []

    rec = ecAuthPath(
        ec_authpath_name = request.POST['ec_authpath_name'],
        ec_authpath_value = request.POST['ec_authpath_value']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_authpath_name'] = rec.ec_authpath_name
    jrec['ec_authpath_value'] = rec.ec_authpath_value
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# settings tables ecAuthPath
# -----------------------------------
def list_ostypes(request):
    response = {}
    data = []

    recs = ecOSTypes.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_ostype'] = rec.ec_ostype
        jrec['ec_disk_type'] = rec.ec_disk_type
        jrec['ec_nic_type'] = rec.ec_nic_type
        jrec['ec_audio_para'] = rec.ec_audio_para
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def ostype_optionlist(request):
    response = {}
    data = []

    recs = ecOSTypes.objects.all()
    for rec in recs:
        jrec = {}
        jrec['DisplayText'] = rec.ec_ostype
        jrec['Value'] = rec.ec_ostype
        data.append(jrec)

    response['Options'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_ostypes(request):
    response = {}
    data = []

    rec = ecOSTypes.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_ostypes(request):
    response = {}

    rec = ecOSTypes.objects.get(id=request.POST['id']);
    rec.ec_ostype = request.POST['ec_ostype']
    rec.ec_disk_type = request.POST['ec_disk_type']
    rec.ec_nic_type = request.POST['ec_nic_type']
    rec.ec_audio_para = request.POST['ec_audio_para']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_ostypes(request):
    response = {}
    data = []

    rec = ecOSTypes(
        ec_ostype = request.POST['ec_ostype'],
        ec_disk_type = request.POST['ec_disk_type'],
        ec_nic_type = request.POST['ec_nic_type'],
        ec_audio_para = request.POST['ec_audio_para'],
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_ostype'] = rec.ec_ostype
    jrec['ec_disk_type'] = rec.ec_disk_type
    jrec['ec_nic_type'] = rec.ec_nic_type
    jrec['ec_audio_para'] = rec.ec_audio_para

    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


# settings tables ecRBAC
# -----------------------------------
def list_rbac(request):
    response = {}

    data = []

    recs = ecRBAC.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['ec_rbac_name'] = rec.ec_rbac_name
        jrec['ec_rbac_permision'] = rec.ec_rbac_permision
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_rbac(request):
    response = {}

    rec = ecRBAC.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_rbac(request):
    response = {}
    data = []

    rec = ecRBAC.objects.get(id=request.POST['id'])
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.ec_rbac_name = request.POST['ec_rbac_name']
    rec.ec_rbac_permision = request.POST['ec_rbac_permision']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_rbac(request):
    response = {}
    data = []

    rec= ecRBAC(
        ec_authpath_name = request.POST['ec_authpath_name'],
        ec_rbac_name = request.POST['ec_rbac_name'],
        ec_rbac_permision = request.POST['ec_rbac_permision']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_authpath_name'] = rec.ec_authpath_name
    jrec['ec_rbac_name'] = rec.ec_rbac_name
    jrec['ec_rbac_permision'] = rec.ec_rbac_permision
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# settings tables ecAuthPath
# -----------------------------------
def list_serverrole(request):
    response = {}
    data = []

    recs = ecServerRole.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_role_name'] = rec.ec_role_name
        jrec['ec_role_value'] = rec.ec_role_value
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def serverrole_optionlist(request):
    response = {}
    data = []

    recs = ecServerRole.objects.all()
    for rec in recs:
        jrec = {}
        jrec['DisplayText'] = rec.ec_role_name
        jrec['Value'] = rec.ec_role_name
        data.append(jrec)

    response['Options'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_serverrole(request):
    response = {}

    rec = ecServerRole.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_serverrole(request):
    response = {}
    data = []

    rec = ecServerRole.objects.get(id=request.POST['id'])
    rec.ec_role_name = request.POST['ec_role_name']
    rec.ec_role_value = request.POST['ec_role_value']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_serverrole(request):
    response = {}
    data = []

    rec = ecServerRole (
        ec_role_name = request.POST['ec_role_name'],
        ec_role_value = request.POST['ec_role_value']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_role_name'] = rec.ec_role_name
    jrec['ec_role_value'] = rec.ec_role_value
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# settings tables ecVMTypes
# -----------------------------------
def list_vmtypes(request):
    response = {}
    data = []

    recs = ecVMTypes.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['name'] = rec.name
        jrec['memory'] = rec.memory
        jrec['cpus'] = rec.cpus
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def vmtpye_optionlist(request):
    response = {}
    data = []

    recs = ecVMTypes.objects.all()
    for rec in recs:
        jrec = {}
        jrec['DisplayText'] = rec.name
        jrec['Value'] = rec.name
        data.append(jrec)

    response['Options'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def delete_vmtypes(request):
    response = {}

    rec = ecVMTypes.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_vmtypes(request):
    response = {}

    rec = ecVMTypes.objects.get(id=request.POST['id'])
    rec.name = request.POST['name']
    rec.memory = request.POST['memory']
    rec.cpus = request.POST['cpus']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_vmtypes(request):
    response = {}
    data = []

    rec = ecVMTypes(
        name = request.POST['name'],
        memory = request.POST['memory'],
        cpus = request.POST['cpus']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['name'] = rec.name
    jrec['memory'] = rec.memory
    jrec['cpus'] = rec.cpus
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# settings tables ecHypervisor
# -----------------------------------
def hypervisor_optionlist(request):
    response = {}
    data = []

    recs = ecHypervisor.objects.all()
    for rec in recs:
        jrec = {}
        jrec['DisplayText'] = rec.hypervisor
        jrec['Value'] = rec.hypervisor
        data.append(jrec)

    response['Options'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_hypervisor(request):
    response = {}
    data = []

    recs = ecHypervisor.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['hypervisor'] = rec.hypervisor
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_hypervisor(request):
    response = {}

    rec = ecHypervisor.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_hypervisor(request):
    response = {}

    rec = ecHypervisor.objects.get(id=request.POST['id'])
    rec.ec_usage = request.POST['hypervisor']

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_hypervisor(request):
    response = {}
    data = []

    rec = ecHypervisor(
        hypervisor = request.POST['hypervisor'],
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['hypervisor'] = rec.hypervisor
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# settings tables ecVMUsage
# -----------------------------------
def list_vmusage(request):
    response = {}
    data = []

    recs = ecVMUsages.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_usage'] = rec.ec_usage
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def vmusage_optionlist(request):
    response = {}
    data = []

    recs = ecVMUsages.objects.all()
    for rec in recs:
        jrec = {}
        jrec['DisplayText'] = rec.ec_usage
        jrec['Value'] = rec.ec_usage
        data.append(jrec)

    response['Options'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_vmusage(request):
    response = {}

    rec = ecVMUsages.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_vmusage(request):
    response = {}

    rec = ecVMUsages.objects.get(id=request.POST['id'])
    rec.ec_usage = request.POST['ec_usage']

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_vmusage(request):
    response = {}
    data = []

    rec = ecVMUsages(
        ec_usage = request.POST['ec_usage'],
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_usage'] = rec.ec_usage
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")



def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]

def autoFindNewAddImage():

    local_images = get_immediate_subdirectories('/storage/images/')

    imageList = ecImages.objects.only("ecid")
    server_images = []
    for imgobj in imageList:
        server_images.append(imgobj.ecid)

    for local_image in local_images:
        if local_image in server_images:
            pass
        else:
            imgfile_path = '/storage/images/' + local_image + "/machine"
            if not os.path.exists(imgfile_path):
                logger.error('Image File Not Exists:%s' % imgfile_path)
                continue

            imgfile_size = os.path.getsize(imgfile_path) / (1024.0 * 1024 * 1024)
            imgfile_size = round(imgfile_size, 2)
            rec = ecImages(
                ecid = local_image,
                name = local_image,
                size = imgfile_size,
            )
            rec.save()

            # create version file for this image
            WriteImageVersionFile(local_image, '1.0.0')

            # add default permission for this image
            rec = ecImages_auth(
                ecid = local_image,
                role_value = "eduCloud.admin",
                read = True,
                write = True,
                execute = True,
                create = True,
                delete = True,
            )
            rec.save()

# core table function for ecClusterNetMode
def list_cc_resource_by_id(request, recid):
    response = {}
    data = []

    rec = ecCCResources.objects.get(id=recid)

    jrec = {}
    jrec['id'] = rec.id
    jrec['ccip'] = rec.ccip
    jrec['ccname'] = rec.ccname
    jrec['network_mode'] = rec.network_mode
    jrec['portRange']=rec.portRange
    jrec['publicIPRange'] = rec.publicIPRange
    jrec['privateIPRange'] = rec.privateIPRange
    jrec['available_Resource'] = rec.available_Resource
    jrec['used_Resource'] = rec.used_Resource
    data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_cc_resource(request):
    response = {}
    data = []

    recs = ecCCResources.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ccip'] = rec.ccip
        jrec['ccname'] = rec.ccname
        jrec['network_mode'] = rec.network_mode
        jrec['portRange']=rec.portRange
        jrec['publicIPRange'] = rec.publicIPRange
        jrec['privateIPRange'] = rec.privateIPRange
        jrec['available_Resource'] = rec.available_Resource
        jrec['used_Resource'] = rec.used_Resource
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def delete_cc_resource(request):
    response = {}

    rec = ecCCResources.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# auto generate available resource for CC
def udate_cc_resource_available_resource(id):
    pass

def update_cc_resource(request):
    response = {}

    rec = ecCCResources.objects.get(id=request.POST['id'])
    rec.ccip = request.POST['ccip']
    rec.ccname = request.POST['ccname']
    rec.network_mode = request.POST['network_mode']
    rec.portRange = request.POST['portRange']
    rec.publicIPRange = request.POST['publicIPRange']
    rec.privateIPRange = request.POST['privateIPRange']
    rec.save()

    udate_cc_resource_available_resource(request.POST['id'])

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_cc_resource(request):
    pass


def list_cc_servers(request):
    ua_admin = ecAccount.objects.get(userid=request.user)
    ua_admin_role_value = ecAuthPath.objects.get(ec_authpath_name = ua_admin.ec_authpath_name)
    role_prefix = ua_admin_role_value.ec_authpath_value.split('.admin')[0]

    response = {}
    data = []

    f_ccname = request.POST['ccname']
    f_ip = request.POST['ip']

    if len(f_ccname) > 0 and len(f_ip) > 0:
        recs = ecServers.objects.filter(ccname__contains=f_ccname, ip0__contains=f_ip, role='cc')
    else:
        if len(f_ccname) > 0:
            recs = ecServers.objects.filter(ccname__contains=f_ccname, role='cc')
        elif len(f_ip) > 0:
            recs = ecServers.objects.filter(ip0__contains=f_ip, role='cc')
        else:
            recs = ecServers.objects.filter(role='cc')

    for rec in recs:
        sobjs = ecServers_auth.objects.filter(srole='cc', mac0=rec.mac0, role_value__contains=role_prefix)
        if sobjs.count() == 0:
            continue

        jrec = {}
        jrec['id'] = rec.id
        jrec['role'] = rec.role
        jrec['eip']  = rec.eip
        jrec['ip0'] = rec.ip0
        jrec['ip1']=rec.ip1
        jrec['ip2'] = rec.ip2
        jrec['ip3'] = rec.ip3
        jrec['mac0'] = rec.mac0
        jrec['mac1']=rec.mac1
        jrec['mac2'] = rec.mac2
        jrec['mac3'] = rec.mac3
        jrec['name'] = rec.name
        jrec['location'] = rec.location
        jrec['cores'] = rec.cpu_cores
        jrec['memory'] = rec.memory
        jrec['disk'] = rec.disk
        jrec['ccname'] = rec.ccname
        jrec['location'] = rec.location

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_nc_servers(request):
    ua_admin = ecAccount.objects.get(userid=request.user)
    ua_admin_role_value = ecAuthPath.objects.get(ec_authpath_name = ua_admin.ec_authpath_name)
    role_prefix = ua_admin_role_value.ec_authpath_value.split('.admin')[0]

    response = {}
    data = []
    f_ccname = request.POST['ccname']
    f_ip = request.POST['ip']

    # step 1 : get all cc
    cc_list = ecServers.objects.filter(role='cc')
    for ccobj in cc_list:
        # step 2 : check filter
        if len(f_ccname) > 0 and ccobj.ccname.find(f_ccname) < 0:
            continue

        # step 3 : check permission
        sobjs = ecServers_auth.objects.filter(srole='cc', mac0=ccobj.mac0, role_value__contains=role_prefix)
        if sobjs.count() == 0:
            continue

        # step 4:  now this cluster is authorized to manage
        if len(f_ip) > 0:
            recs = ecServers.objects.filter(ip0__contains=f_ip, role='nc', ccname=ccobj.ccname)
        else:
            recs = ecServers.objects.filter(role='nc', ccname=ccobj.ccname)

        for rec in recs:
            jrec = {}
            jrec['id'] = rec.id
            jrec['role'] = rec.role
            jrec['eip']  = rec.eip
            jrec['ip0'] = rec.ip0
            jrec['ip1']=rec.ip1
            jrec['ip2'] = rec.ip2
            jrec['ip3'] = rec.ip3
            jrec['mac0'] = rec.mac0
            jrec['mac1']=rec.mac1
            jrec['mac2'] = rec.mac2
            jrec['mac3'] = rec.mac3
            jrec['name'] = rec.name
            jrec['location'] = rec.location
            jrec['cores'] = rec.cpu_cores
            jrec['memory'] = rec.memory
            jrec['disk'] = rec.disk
            jrec['ccname'] = rec.ccname
            jrec['location'] = rec.location
            jrec['hypervisor'] = rec.hypervisor

            data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# core table functions for ecServers
def list_servers_by_role(request, roletype):
    if roletype == 'cc':
        return list_cc_servers(request)

    if roletype == 'nc':
        return list_nc_servers(request)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_servers(request):
    response = {}
    data = []

    recs = ecServers.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['role'] = rec.role
        jrec['eip']  = rec.eip
        jrec['ip0'] = rec.ip0
        jrec['ip1'] = rec.ip1
        jrec['ip2'] = rec.ip2
        jrec['ip3'] = rec.ip3
        jrec['mac0'] = rec.mac0
        jrec['mac1']=rec.mac1
        jrec['mac2'] = rec.mac2
        jrec['mac3'] = rec.mac3
        jrec['name'] = rec.name
        jrec['location'] = rec.location
        jrec['cores'] = rec.cpu_cores
        jrec['memory'] = rec.memory
        jrec['disk'] = rec.disk
        jrec['ccname'] = rec.ccname
        jrec['location'] = rec.location

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_servers(request):
    response = {}

    rec = ecServers.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_servers(request):
    response = {}

    rec = ecServers.objects.get(id=request.POST['id'])
    rec.name = request.POST['name']
    rec.location = request.POST['location']

    rec.save()

    udate_cc_resource_available_resource(request.POST['id'])

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_servers(request):
    pass


def list_ethers(request, cc_name):
    response = {}
    data = []

    recs = ecDHCPEthers.objects.filter(ccname=cc_name)

    for rec in recs:
        jrec = {}
        jrec['id']          = rec.id
        jrec['ccname']      = rec.ccname
        jrec['mac']         = rec.mac
        jrec['ip']          = rec.ip
        jrec['ex_web_port'] = rec.ex_web_proxy_port
        jrec['insid']       = rec.insid

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_ethers(request):
    response = {}

    rec = ecDHCPEthers.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_ethers(request):
    response = {}

    rec = ecDHCPEthers.objects.get(id=request.POST['id'])
    rec.ip                  = request.POST['ip']
    rec.ex_web_proxy_port   = request.POST['ex_web_port']

    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_ethers(request, cc_name):
    response = {}
    data = []

    rec = ecDHCPEthers(
        ccname  = cc_name,
        ip      = request.POST['ip'],
        mac     = randomMAC(),
        ex_web_proxy_port = request.POST['ex_web_port'],
        insid   = '',
    )
    rec.save()

    jrec = {}
    jrec['id']      = rec.id
    jrec['ccname']  = rec.ccname
    jrec['mac']     = rec.mac
    jrec['ip']      = rec.ip
    jrec['insid']   = rec.insid

    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

# ------------------------------------
# core tables for tasks
# ------------------------------------
def list_tasks(request):
    response = {}
    data = []

    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    recs = ectaskTransaction.objects.all()
    for rec in recs:
        if ua_role_value.ec_authpath_value == 'eduCloud.admin':
            pass
        else:
            if rec.user != request.user.username:
                if rec.insid.find('TMP') == 0:
                    continue
                if rec.insid.find('VD') == 0:
                    vdobj = ecVDS.objects.get(insid=rec.insid)
                    if vdobj.creator != request.user.username:
                        continue
                if rec.insid.find('VS') == 0:
                    vsobj = ecVSS.objects.get(insid=rec.insid)
                    if vsobj.creator != request.user.username:
                        continue

        jrec = {}
        jrec['id']       = rec.id
        jrec['tid']      = rec.tid
        jrec['srcimgid'] = rec.srcimgid
        jrec['dstimgid'] = rec.dstimgid
        jrec['insid']    = rec.insid
        jrec['user']     = rec.user
        jrec['phase']    = rec.phase
        jrec['state']    = rec.state
        jrec['completed']= rec.completed
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_tasks(request):
    response = {}

    rec = ectaskTransaction.objects.get(id=request.POST['id'])
    rec.user  = request.POST['user']
    rec.state = request.POST['state']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delet_task_by_id(tid):
    trec = ectaskTransaction.objects.get(tid=tid)

    # # send request to CC to work
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/cc/api/1.0/task/delete' % trec.ccip
    else:
        url = 'http://%s/cc/api/1.0/task/delete' % trec.ccip

    payload = {
        'tid'  :            tid,
        'ncip' :            trec.ncip,
        'runtime_option' :  trec.runtime_option,
    }
    r = requests.post(url, data=payload)
    logger.error("--- --- --- " + url + ":" + r.content)

    releaseRuntimeOptionForImageBuild(tid)
    trec.delete()

    return r

def delete_tasks(request):
    tid = request.POST['tid']
    logger.error("--- --- --- clc delete_tasks %s" % tid)

    r = delet_task_by_id(tid)

    return HttpResponse(r.content, content_type="application/json")

def isLNCActive(mac):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    key = "lnc#%s#status" % mac
    try:
        payload = mc.get(key)
        return 'Online'
    except Exception as e:
        return 'Offlne'

#################################
def list_lnc(request):
    response = {}
    data = []
    f_ccname = request.POST['ccname']
    f_ip = request.POST['ip']

    if len(f_ccname) == 0 and len(f_ip) == 0:
        recs = ecLNC.objects.all()
    elif len(f_ccname) > 0 and len(f_ip) > 0:
        recs = ecLNC.objects.filter(ccname_contains=f_ccname, ip_contains=f_ip)
    elif len(f_ccname) > 0:
        recs = ecLNC.objects.filter(ccname_contains=f_ccname)
    else:
        recs = ecLNC.objects.filter(ip_contains=f_ip)

    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['status'] = isLNCActive(rec.mac)
        jrec['ip']  = rec.ip
        jrec['mac'] = rec.mac
        jrec['cores'] = rec.cpus
        jrec['memory'] = rec.memory
        jrec['disk'] = rec.disk
        jrec['name'] = rec.name
        jrec['location'] = rec.location
        jrec['ccname'] = rec.ccname
        jrec['location'] = rec.location
        jrec['hypervisor'] = rec.hypervisor
        jrec['runtime_option'] = rec.runtime_option

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_lnc(request):
    response = {}

    rec = ecLNC.objects.get(id=request.POST['id']);
    rec.name            = request.POST['name']
    rec.location        = request.POST['location']
    rec.runtime_option  = request.POST['runtime_option']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

#################################

# core tables for images
# ------------------------------------
def list_vds(request):
    response = {}
    data = []

    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    recs = ecVDS.objects.all()

    for rec in recs:
        if ua_role_value.ec_authpath_value != 'eduCloud.admin' and rec.creator != request.user.username:
            continue

        jrec = {}
        jrec['id'] = rec.id
        jrec['insid'] = rec.insid
        jrec['imageid'] = rec.imageid
        jrec['name']=rec.name
        jrec['description'] = rec.description
        jrec['creator'] = rec.creator
        jrec['cc'] = rec.cc_def
        jrec['nc'] = rec.nc_def
        jrec['cpus'] = rec.cpus
        jrec['memory'] = rec.memory

        _tid = '%s:%s:%s' % (rec.imageid, rec.imageid, rec.insid)
        tidrecs = ectaskTransaction.objects.filter(tid=_tid)
        if tidrecs.count() == 0:
            jrec['state'] = 'stopped'
        else:
            jrec['state'] = '%s:%s' % (tidrecs[0].phase, tidrecs[0].state)

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_vds(request):
    response = {}

    vds_rec = ecVDS.objects.get(insid=request.POST['insid'])
    _tid = '%s:%s:%s' % (vds_rec.imageid, vds_rec.imageid, vds_rec.insid)

    tid_recs = ectaskTransaction.objects.filter(tid=_tid)
    if tid_recs.count() != 0 :
        response['Result'] = 'FAIL'
        response['errormsg'] = "Need to delete this VM's running task first"
    else:
        # delete vds_auth records
        ecVDS_auth.objects.filter(insid=request.POST['insid']).delete()
        vds_rec.delete()
        response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_vds(request):
    pass

def create_vds(request):
    response = {}
    recs = ecVDS.objects.filter(insid = request.POST['insid'])
    if recs.count() == 0:
        new_vm = ecVDS(
            insid       = request.POST['insid'],
            imageid     = request.POST['imageid'],
            name        = request.POST['name'],
            description = request.POST['description'],
            creator     = request.user,
            cc_def      = request.POST['cc_def'],
            nc_def      = request.POST['nc_def'],
            cpus        = request.POST['cpus'],
            memory      = request.POST['mems'],
            hypervisor  = request.POST['hypervisor'],
        )
        new_vm.save()
        logger.error("create new vds record --- OK")

        # update ecVDS_auth table
        new_vm_auth = ecVDS_auth(
            insid   =   request.POST['insid'],
            role_value  =   'eduCloud.admin',
            read        =   True,
            write       =   True,
            execute     =   True,
            create      =   True,
            delete      =   True,
        )
        new_vm_auth.save()
        logger.error("create new vds record1 --- OK")

        ua = ecAccount.objects.get(userid=request.user)
        role = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
        if role.ec_authpath_value != 'eduCloud.admin':
            new_vm_auth = ecVDS_auth(
                insid   =   request.POST['insid'],
                role_value  =   ua.ec_authpath_name,
                read        =   True,
                write       =   True,
                execute     =   True,
                create      =   True,
                delete      =   True,
            )
            new_vm_auth.save()
            logger.error("create new vds record2 --- OK")

    else:
        old_vm = ecVDS.objects.get(insid = request.POST['insid'])
        old_vm.name        = request.POST['name']
        old_vm.description = request.POST['description']
        old_vm.cc_def      = request.POST['cc_def']
        old_vm.nc_def      = request.POST['nc_def']
        old_vm.cpus        = request.POST['cpus']
        old_vm.memory      = request.POST['mems']
        old_vm.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_vss(request):
    response = {}
    data = []

    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    recs = ecVSS.objects.all()

    for rec in recs:
        if ua_role_value.ec_authpath_value != 'eduCloud.admin' and rec.creator != request.user.username:
            continue

        jrec = {}
        jrec['id'] = rec.id
        jrec['insid'] = rec.insid
        jrec['imageid'] = rec.imageid
        jrec['name']=rec.name
        jrec['description'] = rec.description
        jrec['creator'] = rec.creator
        jrec['cc'] = rec.cc_def
        jrec['nc'] = rec.nc_def
        jrec['cpus'] = rec.cpus
        jrec['memory'] = rec.memory
        jrec['mac'] = rec.mac

        _tid = '%s:%s:%s' % (rec.imageid, rec.imageid, rec.insid)
        tidrecs = ectaskTransaction.objects.filter(tid=_tid)
        if tidrecs.count() == 0:
            jrec['state'] = 'stopped'
        else:
            jrec['state'] = '%s:%s' % (tidrecs[0].phase, tidrecs[0].state)
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_vss(request):
    response = {}

    vss_rec = ecVSS.objects.get(insid=request.POST['insid'])
    _tid = '%s:%s:%s' % (vss_rec.imageid, vss_rec.imageid, vss_rec.insid)

    tid_recs = ectaskTransaction.objects.filter(tid=_tid)
    if tid_recs.count() != 0 :
        response['Result'] = 'FAIL'
        response['errormsg'] = "Need to delete this VM's running task first"
    else:
        # delete vds_auth records
        ecVSS_auth.objects.filter(insid=request.POST['insid']).delete()
        vss_rec.delete()
        # delete database file
        dbpath = '/storage/space/database/instances/%s' %  request.POST['insid']
        if os.path.exists(dbpath):
            shutil.rmtree(dbpath)

        response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_vss(request):
    pass

def create_vss(request):
    response = {}
    recs = ecVSS.objects.filter(insid = request.POST['insid'])
    if recs.count() == 0:
        new_vm = ecVSS(
            insid       = request.POST['insid'],
            imageid     = request.POST['imageid'],
            name        = request.POST['name'],
            description = request.POST['description'],
            creator     = request.user,
            cc_def      = request.POST['cc_def'],
            nc_def      = request.POST['nc_def'],
            cpus        = request.POST['cpus'],
            memory        = request.POST['mems'],
            mac         = request.POST['mac'],
            hypervisor  = request.POST['hypervisor'],
        )
        new_vm.save()
        logger.error("create new vss record --- OK")

        new_vm_auth = ecVSS_auth(
            insid   =   request.POST['insid'],
            role_value  =   'eduCloud.admin',
            read        =   True,
            write       =   True,
            execute     =   True,
            create      =   True,
            delete      =   True,
        )
        new_vm_auth.save()
        logger.error("create new vm_auth record1 --- OK")

        ua = ecAccount.objects.get(userid=request.user)
        role = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
        if role.ec_authpath_value != 'eduCloud.admin':
            new_vm_auth = ecVDS_auth(
                insid   =   request.POST['insid'],
                role_value  =   ua.ec_authpath_name,
                read        =   True,
                write       =   True,
                execute     =   True,
                create      =   True,
                delete      =   True,
            )
            new_vm_auth.save()
            logger.error("create new vm_auth record2 --- OK")

        # prepare database file
        srcdb = '/storage/space/database/images/%s/database'    % request.POST['imageid']
        dstdb = '/storage/space/database/instances/%s/database' % request.POST['insid']
        if not os.path.exists(dstdb):
            cmd_line = "vboxmanage clonehd %s %s" % (srcdb, dstdb)
            commands.getoutput(cmd_line)
            logger.error("clone instances database --- OK")

    else:
        old_vm = ecVSS.objects.get(insid = request.POST['insid'])
        old_mac = old_vm.mac
        old_vm.name        = request.POST['name']
        old_vm.description = request.POST['description']
        old_vm.cc_def      = request.POST['cc_def']
        old_vm.nc_def      = request.POST['nc_def']
        old_vm.cpus        = request.POST['cpus']
        old_vm.memory      = request.POST['mems']
        old_vm.mac         = request.POST['mac']
        old_vm.save()

        # update ecDHCPEthers table
        if old_mac != 'any':
            ether = ecDHCPEthers.objects.get(mac=old_mac)
            ether.insid = ''
            ether.save()

        if request.POST['mac'] != 'any':
            ether = ecDHCPEthers.objects.get(mac=old_vm.mac)
            ether.insid = old_vm.mac
            ether.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_images(request):
    autoFindNewAddImage()

    response = {}
    data = []

    f_imgname = request.POST['name']
    f_imgostype = request.POST['ostype']

    if len(f_imgname) > 0 and len(f_imgostype) > 0:
        recs = ecImages.objects.filter(name__contains=f_imgname, ostype__contains=f_imgostype)
    else:
        if len(f_imgname) > 0:
            recs = ecImages.objects.filter(name__contains=f_imgname)
        elif len(f_imgostype) > 0:
            recs = ecImages.objects.filter(ostype__contains=f_imgostype)
        else:
            recs = ecImages.objects.all()

    # get current user's role
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    for rec in recs:
        objs = ecImages_auth.objects.filter(ecid=rec.ecid, role_value=ua_role_value.ec_authpath_value )
        if objs.count() > 0 and objs[0].read == True:
            jrec = {}
            jrec['id'] = rec.id
            jrec['ecid'] = rec.ecid
            jrec['name'] = rec.name
            jrec['ostype']=rec.ostype
            jrec['usage'] = rec.img_usage
            jrec['hypervisor'] = rec.hypervisor
            jrec['description'] = rec.description
            jrec['version'] = ReadImageVersionFile(rec.ecid)
            jrec['size'] = rec.size
            data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_images(request):
    response = {}
    rec = ecImages.objects.get(id=request.POST['id'])

    # delete image files
    imgpath = '/storage/images/' + rec.ecid
    if os.path.exists(imgpath):
        shutil.rmtree(imgpath)
    if rec.img_usage == 'server':
        dbpath = '/storage/space/database/images/' + rec.ecid
        if os.path.exists(dbpath):
           shutil.rmtree(dbpath)

    # delete image records
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_images(request):
    response = {}

    rec = ecImages.objects.get(id=request.POST['id'])
    rec.name = request.POST['name']
    rec.ostype = request.POST['ostype']
    rec.img_usage = request.POST['usage']
    rec.hypervisor = request.POST['hypervisor']
    rec.description = request.POST['description']
    rec.save()

    if rec.img_usage == 'server':
        dstfile = '/storage/space/database/images/%s/database' % rec.ecid
        if not os.path.exists(dstfile):
            srcfile = '/storage/images/database'
            cmd_line = "vboxmanage clonehd %s %s" % (srcfile, dstfile)
            out = commands.getoutput(cmd_line)
            logger.error("clone server databae for %s = %s" % (rec.ecid, out))

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def create_images(request):
    response = {}
    data = []

    rec = ecImages(
        ecid = request.POST['ecid'],
        name = request.POST['name'],
        ostype = request.POST['ostype'],
        img_usage = request.POST['usage'],
        hypervisor = request.POST['hypervisor'],
        description = request.POST['description'],
        version = request.POST['version'],
        size = request.POST['size']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ecid'] = rec.ecid
    jrec['name'] = rec.name
    jrec['ostype']=rec.ostype
    jrec['usage'] = rec.img_usage
    jrec['hypervisor'] = rec.hypervisor
    jrec['description'] = rec.description
    jrec['version'] = rec.version
    jrec['size'] = rec.size
    data.append(jrec)

    response['Result'] = 'OK'
    response['Record'] = data

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_inactive_account(request):
    response = {}
    data = []

    ec_username = request.POST['ec_username']
    ec_displayname = request.POST['ec_displayname']

    if len(ec_username) > 0:
        users = User.objects.filter(is_active=0, username__contains=ec_username)
    else:
        users = User.objects.filter(is_active=0)

    for u in users:
        if len(ec_displayname):
            ecuser = ecAccount.objects.filter(userid=u.username, showname__contains=ec_displayname)
        else:
            ecuser = ecAccount.objects.filter(userid=u.username)
        if ecuser.count() == 0:
            continue
        jrec = {}
        jrec['id'] = u.id
        jrec['ec_username'] = u.username
        jrec['ec_displayname'] = ecuser[0].showname
        jrec['ec_email'] = u.email
        jrec['ec_phone'] = ecuser[0].phone
        jrec['ec_supper_user']= u.is_superuser
        jrec['ec_authpath_name'] = ecuser[0].ec_authpath_name
        jrec['vdpara'] = ecuser[0].vdpara
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_active_account(request):
    ua_admin = ecAccount.objects.get(userid=request.user)
    ua_admin_role_value = ecAuthPath.objects.get(ec_authpath_name = ua_admin.ec_authpath_name)
    role_prefix = ua_admin_role_value.ec_authpath_value.split('.admin')[0]

    response = {}
    data = []

    ec_username = request.POST['ec_username']
    ec_displayname = request.POST['ec_displayname']

    if len(ec_username) > 0:
        users = User.objects.filter(is_active=1, username__contains=ec_username)
    else:
        users = User.objects.filter(is_active=1)

    for u in users:
        if len(ec_displayname):
            ecuser = ecAccount.objects.filter(userid=u.username, showname__contains=ec_displayname)
        else:
            ecuser = ecAccount.objects.filter(userid=u.username)
        if ecuser.count() == 0:
            continue

        try:
            ecuser_role_value = ecAuthPath.objects.get(ec_authpath_name = ecuser[0].ec_authpath_name)
            if not ecuser_role_value.ec_authpath_value.startswith(role_prefix):
                continue
        except:
            continue

        jrec = {}
        jrec['id'] = u.id
        jrec['ec_username'] = u.username
        jrec['ec_displayname'] = ecuser[0].showname
        jrec['ec_email'] = u.email
        jrec['ec_phone'] = ecuser[0].phone
        jrec['ec_supper_user']= u.is_superuser
        jrec['ec_authpath_name'] = ecuser[0].ec_authpath_name
        jrec['vdpara'] = ecuser[0].vdpara
        jrec['ec_desc'] = ecuser[0].description
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_active_account(request):
    response = {}

    u = User.objects.get(id=request.POST['id'])
    ecu = ecAccount.objects.get(userid=u.username)
    virtapp_removeAccount2AD(u.username)
    delUserPrvDataDir(ecu.userid)
    u.delete()
    ecu.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_active_account(request):
    response = {}

    u = User.objects.get(id=request.POST['id'])
    ecu = ecAccount.objects.get(userid=u.username)

    ecu.showname = request.POST['ec_displayname']
    u.email = request.POST['ec_email']
    ecu.phone = request.POST['ec_phone']
    u.is_superuser = request.POST['ec_supper_user']
    ecu.ec_authpath_name = request.POST['ec_authpath_name']
    ecu.vdpara = request.POST['vdpara']
    ecu.description = request.POST['ec_desc']

    u.save()
    ecu.save()

    _vdpara = json.loads(ecu.vdpara)
    virtapp_updateAccount2AD(u.username, _vdpara['vapp'])

    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


#################################################################################
# API Version 1.0 for image build & modify
#################################################################################
def register_lnc(request):
    recs = ecLNC.objects.filter(mac=request.POST['mac'])
    if recs.count() > 0:
        if recs[0].ccname == request.POST['ccname']:
            # update existing record
            rec = ecLNC.objects.get(mac=request.POST['mac'])
            rec.ip          = request.POST['ip']

            rec.name        = request.POST['name']
            rec.ccname      = request.POST['ccname']
            rec.location    = request.POST['location']

            rec.cores       = request.POST['cores']
            rec.memory      = request.POST['memory']
            rec.disk        = request.POST['disk']
            rec.runtime_option = request.POST['runtime_option']
            rec.save()
        else:
            # duplicate register
            logger.error(" duplicated lnc registration from %s." % request.POST['ip'])
    else:
        rec = ecLNC(
            mac         = request.POST['mac'],
            ip          = request.POST['ip'],

            name        = request.POST['name'],
            ccname      = request.POST['ccname'],
            location    = request.POST['location'],

            cores       = request.POST['cores'],
            memory      = request.POST['memory'],
            disk        = request.POST['disk'],
            runtime_option = request.POST['runtime_opiton'],
        )
        rec.save()

        auth_rec = ecLNC_auth(
            mac0        =   request.POST['mac'],
            role_value  =   'eduCloud.admin',
            read        =   True,
            write       =   True,
            execute     =   True,
            create      =   True,
            delete      =   True,
        )
        auth_rec.save()

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def register_terminal(request):
    recs = ecTerminal.objects.filter(mac=request.POST['mac'])
    if recs.count() > 0:
        # update existing record
        rec = ecTerminal.objects.get(mac=request.POST['mac'])
        rec.ip          = request.POST['ip']
        rec.mac         = request.POST['mac']

        rec.name        = request.POST['name']
        rec.osname      = request.POST['osname']
        rec.location    = request.POST['location']

        rec.cores       = request.POST['cores']
        rec.memory      = request.POST['memory']
        rec.disk        = request.POST['disk']

        rec.save()
    else:
        rec = ecLNC(
            mac         = request.POST['mac'],
            ip          = request.POST['ip'],

            name        = request.POST['name'],
            osname      = request.POST['osname'],
            location    = request.POST['location'],

            cores       = request.POST['cores'],
            memory      = request.POST['memory'],
            disk        = request.POST['disk'],

        )
        rec.save()

        auth_rec = ecTerminal_auth(
            mac0        =   request.POST['mac'],
            role_value  =   'eduCloud.admin',
            read        =   True,
            write       =   True,
            execute     =   True,
            create      =   True,
            delete      =   True,
        )
        auth_rec.save()

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_ncs(request):

    ncs = ecServers.objects.filter(role='nc', ccname=request.POST['ccname'])
    ncsips = []
    for nc in ncs:
        ncsips.append(nc.ip0)

    response = {}
    response['Result'] = 'OK'
    response['ncs'] = ncsips
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_server_record(request, rec):
    rec.role   = request.POST['role']
    rec.name   = request.POST['name']
    rec.cpu_cores   = request.POST['cores']
    rec.memory = request.POST['memory']
    rec.disk   = request.POST['disk']
    # rec.eip    = request.POST['exip']
    rec.ip0    = request.POST['ip0']
    rec.ip1    = request.POST['ip1']
    rec.ip2    = request.POST['ip2']
    rec.ip3    = request.POST['ip3']
    rec.mac0   = request.POST['mac0']
    rec.mac1   = request.POST['mac1']
    rec.mac2   = request.POST['mac2']
    rec.mac3   = request.POST['mac3']
    rec.ccname = request.POST['ccname']
    rec.hypervisor = request.POST['hypervisor']
    rec.save()

def isTNCActive(mac):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    key = "tnc#%s#status" % mac
    try:
        payload = mc.get(key)
        return 'Online'
    except Exception as e:
        return 'Offlne'

def list_tnc(request):
    response = {}
    data = []
    f_ip = request.POST['ip']

    if len(f_ip) > 0:
        recs = ecTerminal.objects.filter(ip_contains=f_ip)
    else:
        recs = ecTerminal.objects.all()

    for rec in recs:
        jrec = {}
        jrec['status'] = isTNCActive(rec.mac)
        jrec['id'] = rec.id
        jrec['ip']  = rec.ip
        jrec['mac'] = rec.mac
        jrec['cores'] = rec.cpus
        jrec['memory'] = rec.memory
        jrec['disk'] = rec.disk
        jrec['osname'] = rec.osname
        jrec['name'] = rec.name
        jrec['location'] = rec.location

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def update_tnc(request):
    pass

def add_new_server(request):
    rec = ecServers(
            role   = request.POST['role'],
            name   = request.POST['name'],
            cpu_cores   = request.POST['cores'],
            memory = request.POST['memory'],
            disk   = request.POST['disk'],
            eip    = request.POST['exip'],
            ip0    = request.POST['ip0'],
            ip1    = request.POST['ip1'],
            ip2    = request.POST['ip2'],
            ip3    = request.POST['ip3'],
            mac0   = request.POST['mac0'],
            mac1   = request.POST['mac1'],
            mac2   = request.POST['mac2'],
            mac3   = request.POST['mac3'],
            ccname = request.POST['ccname'],
            hypervisor = request.POST['hypervisor'],
    )
    rec.save()

    # add auth permission for new
    auth_rec = ecServers_auth(
        mac0        =   request.POST['mac0'],
        srole       =   request.POST['role'],
        role_value  =   'eduCloud.admin',
        read        =   True,
        write       =   True,
        execute     =   True,
        create      =   True,
        delete      =   True,
    )
    auth_rec.save()

    if request.POST['role'] == 'cc':
        res_rec = ecCCResources(
            ccmac0              = request.POST['mac0'],
            ccname              = request.POST['ccname'],
            cc_usage            = "rvd",

            rdp_port_pool_def   = "3400-3499",
            rdp_port_pool_list  = json.dumps(SortedList(range(3389,4389)).as_list()),
            used_rdp_ports      = json.dumps([]),

            network_mode        = 'flat',

            dhcp_service        = 'external',   # {none, external, private}
            dhcp_pool_def       = '192.168.0.100-192.168.0.254',
            dhcp_interface      = 'eth0',

            pub_ip_pool_def     = '192.168.0.100-192.168.0.254',
            pub_ip_pool_list    = '',
            used_pub_ip         = '',
        )
        res_rec.save()

def register_server(request):
    if request.POST['role'] == 'clc':
        recs = ecServers.objects.filter(role=request.POST['role'])
        if recs.count() > 0:
            if recs[0].mac0 == request.POST['mac0']:
                # update existing record
                update_server_record(request, recs[0])
            else:
                # duplicate clc register
                logger.error(" duplicated CLC registration from %s." % request.POST['ip0'])
        else:
            # new record
            add_new_server(request)
    elif request.POST['role'] == 'walrus':
        recs = ecServers.objects.filter(role=request.POST['role'])
        if recs.count() > 0:
            if recs[0].mac0 == request.POST['mac0']:
                # update existing record
                update_server_record(request, recs[0])
            else:
                # duplicate clc register
                logger.error(" duplicated Walrus registration from %s." % request.POST['ip0'])
        else:
            # new record
            add_new_server(request)
    elif request.POST['role'] == 'cc':
        recs = ecServers.objects.filter(role=request.POST['role'], ccname=request.POST['ccname'])
        if recs.count() > 0:
            if recs[0].mac0 == request.POST['mac0']:
                # update existing record
                logger.error('------ update_server_record')
                update_server_record(request, recs[0])
            else:
                # duplicate clc register
                logger.error(" duplicated CC registration from %s." % request.POST['ip0'])
        else:
            # new record
            logger.error('------ add_new_server')
            add_new_server(request)
    elif request.POST['role'] == 'nc':
        recs = ecServers.objects.filter(role=request.POST['role'], mac0=request.POST['mac0'])
        if recs.count() > 0:
            if recs[0].ccname == request.POST['ccname']:
                # update existing record
                update_server_record(request, recs[0])
            else:
                # duplicate clc register
                logger.error(" duplicated nc registration from %s." % request.POST['ip0'])
        else:
            # new record
            add_new_server(request)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

#################################################################################
# some common APIs
#################################################################################
def get_walrus_info(request):
    rec = ecServers.objects.get(role='walrus')
    payload = {
        'role':   rec.role,
        'name':   rec.name,
        'cpus':   rec.cpu_cores,
        'memory': rec.memory,
        'disk':   rec.disk,
        'ip0':    rec.ip0,
        'ip1':    rec.ip1,
        'ip2':    rec.ip2,
        'ip3':    rec.ip3,
    }
    response = {}
    response['Result'] = "OK"
    response['data'] = payload
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def get_image_info(request):
    tid = request.POST['tid']
    imgid = tid.split(':')[0]
    insid = tid.split(':')[2]
    version, size = getLocalImageInfo(imgid)
    dbsize = getLocalDatabaseInfo(imgid, insid)

    payload = {
        'version':           version,
        'size':              size,
        'dbsize':            dbsize,
    }

    response = {}
    response['Result'] = "OK"
    response['data'] = payload
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def image_permission_edit(request, srcid):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    if ua_role_value.ec_authpath_value != 'eduCloud.admin':
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _('Only eduCloud.Admin can change image permission!'),
            'suggestion'    : _('Please logon as eduCloud.Admin.'),
        }
        return render(request, 'clc/error.html', context)

    index = 0
    authlist =  ecAuthPath.objects.all()
    roles = []
    for auth in authlist:
        role={}
        role['name']    =auth.ec_authpath_name
        role['value']   = auth.ec_authpath_value
        roles.append(role)

    permsObjs = ecImages_auth.objects.filter(ecid=srcid)
    perms = []
    for perm_obj in permsObjs:
        perm = {}
        perm['id'] = 'perm' +  str(index)
        perm['role_value'] = perm_obj.role_value
        perm['read'] =  perm_obj.read
        perm['write'] = perm_obj.write
        perm['execute'] = perm_obj.execute
        perm['create'] = perm_obj.create
        perm['delete'] = perm_obj.delete
        perms.append(perm)
        index += 1

    rows = len(perms)

    imgobj = ecImages.objects.get(ecid=srcid)

    context = {
        'imgobj': imgobj ,
        'res':    _("Image ") + imgobj.name,
        'roles':  roles,
        'lists':  range(0,rows),
        'next':   rows,
        'perms':  perms,
        'table': 'ecImages',
    }
    return render(request, 'clc/form/permission_edit.html', context)

def image_perm_update(id, data):

    tflist = {
        'true': True,
        'false': False,
    }

    perms = data.split('#')
    for perm in perms:
        if len(perm) > 0:
            auth = perm.split(':')
            _role   = auth[0]
            _read   = tflist[auth[1]]
            _write  = tflist[auth[2]]
            _execute= tflist[auth[3]]
            _create = tflist[auth[4]]
            _delete = tflist[auth[5]]

            try:
                rec = ecImages_auth.objects.get(ecid=id, role_value= _role)
                rec.read    = _read
                rec.write   = _write
                rec.execute = _execute
                rec.create  = _create
                rec.delete  = _delete
                rec.save()
            except:
                rec = ecImages_auth(
                    ecid        = id,
                    role_value  = _role,
                    read        = _read,
                    write       = _write,
                    execute     = _execute,
                    create      = _create,
                    delete      = _delete,
                )
                rec.save()

def server_perm_update(id, data):
    tmp = id.split("&")

    tflist = {
        'true': True,
        'false': False,
    }

    perms = data.split('#')
    for perm in perms:
        if len(perm) > 0:
            auth = perm.split(':')
            _role   = auth[0]
            _read   = tflist[auth[1]]
            _write  = tflist[auth[2]]
            _execute= tflist[auth[3]]
            _create = tflist[auth[4]]
            _delete = tflist[auth[5]]

            try:
                rec = ecServers_auth.objects.get(srole=tmp[0], mac0=tmp[1], role_value= _role)
                rec.read    = _read
                rec.write   = _write
                rec.execute = _execute
                rec.create  = _create
                rec.delete  = _delete
                rec.save()
            except:
                rec = ecServers_auth(
                    srole       = tmp[0],
                    mac0        = tmp[1],
                    role_value  = _role,
                    read        = _read,
                    write       = _write,
                    execute     = _execute,
                    create      = _create,
                    delete      = _delete,
                )
                rec.save()

def vss_perm_update(id, data):

    tflist = {
        'true': True,
        'false': False,
    }

    perms = data.split('#')
    for perm in perms:
        if len(perm) > 0:
            auth = perm.split(':')
            _role   = auth[0]
            _read   = tflist[auth[1]]
            _write  = tflist[auth[2]]
            _execute= tflist[auth[3]]
            _create = tflist[auth[4]]
            _delete = tflist[auth[5]]

            try:
                rec = ecVSS_auth.objects.get(insid=id, role_value= _role)
                rec.read    = _read
                rec.write   = _write
                rec.execute = _execute
                rec.create  = _create
                rec.delete  = _delete
                rec.save()
            except:
                rec = ecVSS_auth(
                    insid       = id,
                    role_value  = _role,
                    read        = _read,
                    write       = _write,
                    execute     = _execute,
                    create      = _create,
                    delete      = _delete,
                )
                rec.save()

def vds_perm_update(id, data):

    tflist = {
        'true': True,
        'false': False,
    }

    perms = data.split('#')
    for perm in perms:
        if len(perm) > 0:
            auth = perm.split(':')
            _role   = auth[0]
            _read   = tflist[auth[1]]
            _write  = tflist[auth[2]]
            _execute= tflist[auth[3]]
            _create = tflist[auth[4]]
            _delete = tflist[auth[5]]

            try:
                rec = ecVDS_auth.objects.get(insid=id, role_value= _role)
                rec.read    = _read
                rec.write   = _write
                rec.execute = _execute
                rec.create  = _create
                rec.delete  = _delete
                rec.save()
            except:
                rec = ecVDS_auth(
                    insid       = id,
                    role_value  = _role,
                    read        = _read,
                    write       = _write,
                    execute     = _execute,
                    create      = _create,
                    delete      = _delete,
                )
                rec.save()

def perm_update(request):
    id = request.POST['id']
    table = request.POST['table']
    data = request.POST['data']

    if table == 'ecImages':
        image_perm_update(id, data)
    elif table == "ecServers":
        server_perm_update(id, data)
    elif table == "ecVSS":
        vss_perm_update(id, data)
    elif table == "ecVDS":
        vds_perm_update(id, data)

    response = {}
    response['Result'] = "OK"
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def eip_update(request):
    _eip = request.POST['eip']
    _mac0 = request.POST['mac0']
    _role = request.POST['role']

    rec = ecServers.objects.get(role=_role, mac0=_mac0)
    rec.eip = _eip
    rec.save()

    response = {}
    response['Result'] = "OK"
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def edit_server_permission_view(request, srole, mac):
    index = 0
    authlist =  ecAuthPath.objects.all()
    roles = []
    for auth in authlist:
        role={}
        role['name']    = auth.ec_authpath_name
        role['value']   = auth.ec_authpath_value
        roles.append(role)

    permsObjs = ecServers_auth.objects.filter(mac0=mac, srole=srole)
    perms = []
    for perm_obj in permsObjs:
        perm = {}
        perm['id'] = 'perm' +  str(index)
        perm['role_value'] = perm_obj.role_value
        perm['read'] =  perm_obj.read
        perm['write'] = perm_obj.write
        perm['execute'] = perm_obj.execute
        perm['create'] = perm_obj.create
        perm['delete'] = perm_obj.delete
        perms.append(perm)
        index += 1

    rows = len(perms)

    sobj = ecServers.objects.get(mac0=mac, role=srole)

    context = {
        'sobj':   sobj,
        'res':    _("Server "),
        'roles':  roles,
        'lists':  range(0,rows),
        'next':   rows,
        'perms':  perms,
        'table': 'ecServers',
    }
    return render(request, 'clc/form/server_permission_edit.html', context)

def edit_vm_permission_view(request, insid):
    index = 0
    authlist =  ecAuthPath.objects.all()
    roles = []
    for auth in authlist:
        role={}
        role['name']    = auth.ec_authpath_name
        role['value']   = auth.ec_authpath_value
        roles.append(role)

    if insid.find('VS') == 0:
        permsObjs = ecVSS_auth.objects.filter(insid=insid)
        sobj = ecVSS.objects.get(insid=insid)
        table = 'ecVSS'
    if insid.find('VD') == 0:
        permsObjs = ecVDS_auth.objects.filter(insid=insid)
        sobj = ecVDS.objects.get(insid=insid)
        table = 'ecVDS'

    perms = []
    for perm_obj in permsObjs:
        perm = {}
        perm['id'] = 'perm' +  str(index)
        perm['role_value'] = perm_obj.role_value
        perm['read'] =  perm_obj.read
        perm['write'] = perm_obj.write
        perm['execute'] = perm_obj.execute
        perm['create'] = perm_obj.create
        perm['delete'] = perm_obj.delete
        perms.append(perm)
        index += 1

    rows = len(perms)

    context = {
        'sobj':   sobj,
        'res':    _("VM "),
        'roles':  roles,
        'lists':  range(0,rows),
        'next':   rows,
        'perms':  perms,
        'table':  table,
    }
    return render(request, 'clc/form/vm_permission_edit.html', context)

def rdp_web_client(request):
    return render(request, 'clc/rdpclient/webclient3.html')

#######################################
### API v1.0 for portal request
#######################################
# def list_sites(request):
#     list_of_sites =[]
#     one_site = {
#         'name': 'First Application',
#         'desc': 'This is the first application we are build this year',
#         'web_url': 'http://www.baidu.com'
#     }
#     second_site = {
#         'name': 'Second Application',
#         'desc': 'This is the Second application we are build this year',
#         'web_url': 'http://www.taobao.com'
#     }
#     third_site = {
#         'name': 'Third Application',
#         'desc': 'This is the Third application we are build this year',
#         'web_url': 'http://www.popsugar.com'
#     }
#     list_of_sites.append(one_site)
#     list_of_sites.append(second_site)
#     list_of_sites.append(third_site)
#
#     response = {}
#     response['Result'] = 'OK'
#     response['data']   = list_of_sites
#     retvalue = json.dumps(response)
#     return HttpResponse(retvalue, content_type="application/json")

def list_sites(request):
    list_of_sites =[]
    vss_objects = ecVSS.objects.all()
    for vs in vss_objects:
        one_site = {}
        one_site['name'] = vs.name
        one_site['desc'] = vs.description
        _tid = '%s:%s:%s' % (vs.imageid, vs.imageid, vs.insid)

        tobjs = ectaskTransaction.objects.filter(tid=_tid)
        if tobjs.count() > 0:
           if tobjs[0].phase == 'editing':
               if tobjs[0].state == 'running' or tobjs[0].state == 'Running':
                   runtime_option = json.loads( tobjs[0].runtime_option )
                   one_site['web_url'] = getValidWebURL(request, runtime_option)
                   list_of_sites.append(one_site)

    response = {}
    response['Result'] = 'OK'
    response['data']   = list_of_sites
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def getUserBySession(session_key):
    from django.contrib.sessions.models import Session
    sobj = Session.objects.get(pk=session_key)
    uid = sobj.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)
    return user

def verifySessionKey(session_key):
    from django.contrib.sessions.models import Session
    sobj = Session.objects.filter(pk=session_key)
    if sobj.count() > 0:
        return True
    else:
        return False

def list_myvapps(uid):
    vapp = []
    userobj = ecAccount.objects.get(userid = uid)
    para = json.loads(userobj.vdpara)
    if para['vapp'] != 'yes':
        return vapp

    # check vapp list available for this user
    return list_my_availed_vapp

def list_myvds(request):
    '''
    :param request:
    :return: list of tvds, including :
             name, description, ostype,
    :        tid, phase, state, mgr_url
    '''

    vds = []
    index = 0
    _user = request.POST['user']
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    imgobjs = ecImages.objects.filter(img_usage='desktop')
    # get current user's role
    ua = ecAccount.objects.get(userid=_user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    for imgobj in imgobjs:
        objs = ecImages_auth.objects.filter(ecid=imgobj.ecid, role_value=ua_role_value.ec_authpath_value )
        if objs.count() > 0 and objs[0].execute == True:
            vd = {}
            vd['ecid']   = imgobj.ecid
            vd['name']   = imgobj.name
            vd['ostype'] = imgobj.ostype
            vd['desc']   = imgobj.description

            trecs = ectaskTransaction.objects.filter(srcimgid=imgobj.ecid, dstimgid=imgobj.ecid, user=_user, insid__contains='TVD')
            if trecs.count() > 0:
                for trec in trecs:
                    vd['tid'] = trec.tid
                    vd['phase'] = trec.phase
                    vd['state'] = trec.state
                    runtime_option = json.loads(trec.runtime_option)
                    vd['mgr_url'] = getValidMgrURL(request, runtime_option)
                    vd['id']  = 'myvd' + str(index)
                    vds.append(vd)
                    index += 1
            else:
                vd['tid'] = ''
                vd['phase'] = ''
                vd['state'] = ''
                vd['mgr_url'] = ''
                vd['id']  = 'myvd' + str(index)
                vds.append(vd)
                index += 1

    trecs = ectaskTransaction.objects.filter(user=_user)
    for trec in trecs:
        insid = trec.insid
        if insid.find('VD') == 0:
            imgobj = ecImages.objects.get(ecid=trec.srcimgid)
            vd = {}
            vd['ecid'] = imgobj.ecid
            vd['name'] = imgobj.name
            vd['ostype'] = imgobj.ostype
            vd['desc'] = imgobj.description

            def_vd = ecVDS.objects.get(insid=insid)
            vd['name'] = def_vd.name
            if len(def_vd.description) > 0:
                vd['desc'] = def_vd.description

            vd['tid'] = trec.tid
            vd['phase'] = trec.phase
            vd['state'] = trec.state
            runtime_option = json.loads(trec.runtime_option)
            vd['mgr_url'] = getValidMgrURL(request, runtime_option)
            vd['id']  = 'myvd' + str(index)
            vds.append(vd)
            index += 1


    response = {}
    response['Result'] = 'OK'
    response['data'] = vds
    logger.error("user %s own virtual desktop as below: %s" %(_user, vds))

    para = json.loads(ua.vdpara)
    if para['vapp'] == 'yes':
        myvapps = list_my_availed_vapp(_user)
        response['vapp'] = myvapps['data']
    else:
        response['vapp'] = []
    logger.error("user %s own virtual app as below: %s" %(_user, response['vapp']))

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def rvd_start(request, srcid, dstid, insid):
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    response = {}

    _tid  = '%s:%s:%s' % (srcid, dstid, insid)

    # if tid exist, just call view
    # else find resource and create tid
    trecs = ectaskTransaction.objects.filter(tid=_tid)
    if trecs.count() > 0:
        response['Result'] = 'OK'
        response['tid']  = _tid
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")
    else:
        _ccip, _ncip, _msg = findVMRunningResource(request, insid)
        if _ncip == None:
            response['Result'] = 'FAIL'
            response['error']  = _msg
            retvalue = json.dumps(response)
            return HttpResponse(retvalue, content_type="application/json")
        else:
            rec = ectaskTransaction(
                 tid         = _tid,
                 srcimgid    = srcid,
                 dstimgid    = dstid,
                 insid       = insid,
                 user        = request.user.username,
                 phase       = 'preparing',
                 state       = "init",
                 progress    = 0,
                 ccip        = _ccip,
                 ncip        = _ncip,
            )
            rec.save()
            runtime_option, error = genRuntimeOptionForImageBuild(_tid)
            if runtime_option == None:
                rec.delete()
                response['Result'] = 'FAIL'
                response['error']  = error
                retvalue = json.dumps(response)
                return HttpResponse(retvalue, content_type="application/json")
            else:
                rec.runtime_option = json.dumps(runtime_option)
                rec.save()

                response['Result'] = 'OK'
                response['tid']  = _tid
                retvalue = json.dumps(response)
                return HttpResponse(retvalue, content_type="application/json")


def rvd_create(request, srcid):
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    response = {}

    # create ectaskTransation Record
    _srcimgid        = srcid
    _dstimageid      = srcid
    _instanceid      = 'TVD' + genHexRandom()
    _tid             = '%s:%s:%s' % (_srcimgid, _dstimageid, _instanceid )

    logger.error("--- --- --- rvd_create %s" % _tid)

    _ccip, _ncip, _msg = findBuildResource(srcid)
    if _ncip == None:
        # not find proper cc,nc for build image
        response['Result'] = 'FAIL'
        response['error']  = _msg
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")
    else:
        if request.user.username =='':
            _user = getUserBySession(_skey)
            _user_name = _user.username
        else:
            _user_name = request.user.username

        rec = ectaskTransaction(
             tid         = _tid,
             srcimgid    = _srcimgid,
             dstimgid    = _dstimageid,
             insid       = _instanceid,
             user        = _user_name,
             phase       = 'preparing',
             state       = "init",
             progress    = 0,
             ccip        = _ccip,
             ncip        = _ncip,
        )
        rec.save()
        runtime_option, error = genRuntimeOptionForImageBuild(_tid)
        if runtime_option == None:
                rec.delete()
                response['Result'] = 'FAIL'
                response['error']  = error
                retvalue = json.dumps(response)
                return HttpResponse(retvalue, content_type="application/json")
        else:
            rec.runtime_option = json.dumps(runtime_option)
            rec.save()

            response['Result'] = 'OK'
            response['tid']  = _tid
            retvalue = json.dumps(response)
            return HttpResponse(retvalue, content_type="application/json")


def rvd_prepare(request, srcid, dstid, insid):
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    return image_create_task_prepare(request, srcid, dstid, insid)

def rvd_getprogress(request, srcid, dstid, insid):
    return image_create_task_getprogress(request, srcid, dstid, insid)

def rvd_run(request, srcid, dstid, insid):
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    return image_create_task_run(request, srcid, dstid, insid)

def rvd_stop(request, srcid, dstid, insid):
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    return image_create_task_stop(request, srcid, dstid, insid)

def rvd_getvmstatus(request, srcid, dstid, insid):
    return image_create_task_getvmstatus(request, srcid, dstid, insid)

def rvd_display(request, srcid, dstid, insid):
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    return vm_display(request, srcid, dstid, insid)

def rvd_get_rdp_para(request, srcid, dstid, insid):
    response = {}

    _tid  = '%s:%s:%s' % (srcid, dstid, insid)

    # if tid exist, just call view
    # else find resource and create tid
    trecs = ectaskTransaction.objects.filter(tid=_tid)
    if trecs.count() > 0:
        runtime_option = json.loads(trecs[0].runtime_option)
        response['Result']     = 'OK'
        response['rdp_ip']     = runtime_option['rdp_ip']
        response['rdp_port']   = runtime_option['rdp_port']
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

def rvd_get_rdp_url(request, srcid, dstid, insid):
    _skey = request.POST['sid']

    result = verifySessionKey(_skey)
    if result == False:
        response = {}
        response['Result'] = 'FAIL'
        response['error'] = 'session is invalide, need logon first'
        retvalue = json.dumps(response)
        return HttpResponse(retvalue, content_type="application/json")

    return rvd_get_rdp_para(request, srcid, dstid, insid)

