# coding=UTF-8

from __future__ import division
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

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

import requests, memcache

logger = getclclogger()

def findLazyNC(cc_name):
    ncs = ecServers.objects.filter(ccname=cc_name, role='nc')
    return ncs[0].ip0

# this is simple algorith, just find the first cc in db
def findLazyCC(srcid):
    rec = ecImages.objects.get(ecid=srcid)
    if rec.usage == "server":
        filter = 'vs'
    else:
        filter = 'rvd'

    ccs = ecCCResources.objects.filter(usage=filter)
    ccip = ccs[0].ccip
    return ccip, ccs[0].ccname

def display_login_window(request):
    return render(request, 'clc/login.html', {})

def user_login(request):
    response = {}
    username = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            response['status'] = "SUCCESS"
            response['url'] = "/clc/index"
            return HttpResponse(json.dumps(response), mimetype='application/json')
        else:
            # Return a 'disabled account' error message
            response['status'] = "FAILURE"
            response['reason'] = "account is disabled"
            return HttpResponse(json.dumps(response), mimetype='application/json')
    else:
        # Return an 'invalid login' error message.
        response['status'] = "FAILURE"
        response['reason'] = "account is invalid"
        return HttpResponse(json.dumps(response), mimetype='application/json')

def user_logout(request):
    logout(request)
    return render(request, 'clc/login.html', {})

@login_required
def index_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "System Run-time Status Overview",
    }
    return render(request, 'clc/overview.html', context)

@login_required
def accounts_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Account Management",
    }
    return render(request, 'clc/accounts.html', context)

@login_required
def images_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Images Management",
    }

    return render(request, 'clc/images.html', context)

@login_required
def computers_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Computer Management",
    }
    return render(request, 'clc/computers.html', context)


@login_required
def hosts_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Hosts Management",
    }
    return render(request, 'clc/hosts.html', context)

@login_required
def settings_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "System Settings Management",
    }
    return render(request, 'clc/settings.html', context)

@login_required
def vss_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Cloud App Management",
    }

    return render(request, 'clc/vss.html', context)

@login_required
def rvds_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Remote Cloud Desktop Management",
    }

    return render(request, 'clc/rvds.html', context)

@login_required
def lvds_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Local Cloud Desktop Management",
    }

    return render(request, 'clc/lvds.html', context)

@login_required
def tasks_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Tasks Management",
    }

    return render(request, 'clc/tasks.html', context)

###################################################################################
# Form
###################################################################################
def generateAvailableResourceforCC(cc_name):
    rec = ecCCResources.objects.get(ccname=cc_name)
    emptyarray = []

    if rec.usage == 'lvd':

        rec.network_mode    = ''
        rec.portRange       = ''
        rec.publicIPRange   = ''
        rec.privateIPRange  = ''
        rec.service_ports       = json.dumps(emptyarray)
        rec.available_rdp_ports = json.dumps(emptyarray)
        rec.used_rdp_ports      = json.dumps(emptyarray)
        rec.available_ips_macs  = json.dumps(emptyarray)
        rec.used_ips_macs       = json.dumps(emptyarray)

    elif rec.usage == 'rvd': # only need port range
        rec.publicIPRange   = ''
        rec.privateIPRange  = ''
        rec.service_ports      = json.dumps(emptyarray)
        rec.available_ips_macs = json.dumps(emptyarray)
        rec.used_ips_macs      = json.dumps(emptyarray)

        portrange = rec.portRange.split('-')
        portrange = range(int(portrange[0]), int(portrange[1]))
        rec.available_rdp_ports = json.dumps(portrange)
        rec.used_rdp_ports = json.dumps(emptyarray)

    elif rec.usage == 'vs':
        portrange = rec.portRange.split('-')
        portrange = range(int(portrange[0]), int(portrange[1]))
        rec.available_rdp_ports = json.dumps(portrange)
        rec.used_rdp_ports = json.dumps(emptyarray)

        if rec.network_mode == "MANUAL":
            rec.publicIPRange   = ''
            rec.privateIPRange  = ''
            rec.service_ports      = json.dumps(emptyarray)
            rec.available_ips_macs = json.dumps(emptyarray)
            rec.used_ips_macs      = json.dumps(emptyarray)
        elif rec.network_mode == "PUBLIC":
            rec.privateIPRange  = ''
            iplist    = rec.publicIPRange.split('-')
            iplist    = ipRange(iplist[0], iplist[1])
            lenght    = len(iplist)

            available_ips_macs = []

            for index in range(0, lenght):
                res = {}
                res['pubip']    = iplist[index]
                res['prvip']    = iplist[index]
                res['mac']      = randomMAC()
                available_ips_macs.append(res)
            rec.available_ips_macs = json.dumps(available_ips_macs)
            rec.used_ips_macs      = json.dumps(emptyarray)
        elif rec.network_mode == "PRIVATE":
            pubiplist    = rec.publicIPRange.split('-')
            pubiplist    = ipRange(pubiplist[0], pubiplist[1])

            prviplist    = rec.privateIPRange.split('-')
            prviplist    = ipRange(prviplist[0], prviplist[1])

            lenght    = min(len(pubiplist), len(prviplist))

            available_ips_macs = []

            for index in range(0, lenght):
                res = {}
                res['pubip']    = pubiplist[index]
                res['prvip']    = prviplist[index]
                res['mac']      = randomMAC()
                available_ips_macs.append(res)
            rec.available_ips_macs = json.dumps(available_ips_macs)
            rec.used_ips_macs      = json.dumps(emptyarray)
    rec.save()

@login_required
def cc_modify_resources(request, cc_name):
    rec = ecCCResources.objects.get(ccname=cc_name)
    if request.method == 'POST':
        rec.usage           = request.POST['usage']
        rec.network_mode    = request.POST['network_mode']
        rec.portRange       = request.POST['port_range']
        rec.publicIPRange   = request.POST['pubip_range']
        rec.privateIPRange  = request.POST['prvip_range']
        rec.service_ports   = request.POST['sport_port']
        rec.save()

        generateAvailableResourceforCC(cc_name)

        response = {}
        response['Result'] = 'OK'

        return HttpResponse(json.dumps(response), mimetype="application/json")
    else:
        context = {
            'pagetitle' : "Configure CC Network Resources",
            'ccres' : rec,
        }

        return render(request, 'clc/form/cc_modify_resource.html', context)

###############################################ti##################################
# create a new images & modify existing image
###################################################################################

# {
#     # general
#     'ostype'            :
#     'usage'             :
#     # hardware
#     'memeory'           :
#     'cpus'              :
#     'disk_type'         :
#     'audio_para'        :
#     # network
#     'netwowrkcards'     :
#     [
#         { 'nic_type': "", 'nic_mac': "" , 'nic_pubip': "", 'nic_prvip'},
#         ... ...
#     ]
#     'publicIP'          :
#     'privateIP'         :
#     'rdp_port'          :
#     'services_ports'    : [ ... ...]
#     'accessURL'         :
#     'mgr_accessURL'     :
#     'run_with_snapshot' : 1, 0
#     'iptable_rules'     :
#     [
#         'rule1',
#         'rule2',
#         ... ...
#     ]
# }


def genRuntimeOptionForImageBuild(transid):
    tidrec = ectaskTransaction.objects.get(tid=transid)

    runtime_option = {}
    runtime_option['iptable_rules'] = []
    runtime_option['networkcards']  = []

    # prepare runtime option
    img_info = ecImages.objects.get(ecid = tidrec.srcimgid)
    runtime_option['ostype']     = img_info.ostype
    runtime_option['usage']      = img_info.usage
    if img_info.usage == "desktop":
        vmtype = 'vdmedium'
    else:
        vmtype = 'vssmall'
    vmtype_info = ecVMTypes.objects.get(name=vmtype)
    runtime_option['memory']     = vmtype_info.memory
    runtime_option['cpus']       = vmtype_info.cpus
    ostype_info = ecOSTypes.objects.get(ec_ostype = img_info.ostype)
    nic_type                     = ostype_info.ec_nic_type
    runtime_option['disk_type']  = ostype_info.ec_disk_type
    runtime_option['audio_para'] = ostype_info.ec_audio_para

    #################################
    # now allocate network resource
    #################################

    ccres_info = ecCCResources.objects.get(ccip = tidrec.ccip)

    ###########################
    # 1. allocate rpd port

    available_rpd_port = json.loads(ccres_info.available_rdp_ports)
    used_rdp_ports     = json.loads(ccres_info.used_rdp_ports)

    if len(available_rpd_port) > 0:
        newport = available_rpd_port[0]
        available_rpd_port.remove(newport)
        used_rdp_ports.append(newport)
        runtime_option['rdp_port'] = newport

        ccres_info.available_rdp_ports = json.dumps(available_rpd_port)
        ccres_info.used_rdp_ports      = json.dumps(used_rdp_ports)
        ccres_info.save()
    else:
        runtime_option['rdp_port'] = ''

    ############################
    # 2. allocate ips, macs
    if ccres_info.usage == 'rvd':
        networkcards = []
        netcard = {}
        netcard['nic_type'] = nic_type
        netcard['nic_mac']  = ''
        netcard['nic_pubip']   = ''
        netcard['nic_prvip']   = ''
        networkcards.append(netcard)
        runtime_option['networkcards'] = networkcards

    elif ccres_info.usage == 'vs':
        available_ips_macs = json.loads(ccres_info.available_ips_macs)
        used_ips_macs      = json.loads(ccres_info.used_ips_macs)
        network_mode       = ccres_info.network_mode

        if len(available_ips_macs) > 0:
            new_ips_macs = available_ips_macs[0]
            available_ips_macs.remove(new_ips_macs)
            used_ips_macs.append(new_ips_macs)

            networkcards = []
            netcard = {}
            netcard['nic_type']     = nic_type
            netcard['nic_mac']      = new_ips_macs['mac']
            netcard['nic_pubip']    = new_ips_macs['pubip']
            netcard['nic_privip']   = new_ips_macs['prvip']
            networkcards.append(netcard)
            runtime_option['networkcards'] = networkcards

            ccres_info.available_ips_macs = json.dumps(available_ips_macs)
            ccres_info.used_ips_macs      = json.dumps(used_ips_macs)
            ccres_info.save()
        else:
            runtime_option['networkcards'] = ''

        runtime_option['publicIP']  = new_ips_macs['pubip']
        runtime_option['privateIP'] = new_ips_macs['prvip']

        service_ports = ccres_info.service_ports
        if service_ports != '':
            runtime_option['services_ports'] = json.loads(service_ports)
        else:
            runtime_option['services_ports'] = ''

        runtime_option['mgr_accessURL'] = runtime_option['publicIP'] + ':' + runtime_option['rdp_port']
        runtime_option['run_with_snapshot'] = 0

        if network_mode == "MANUAL":
            runtime_option['iptable_rules'] = []
        elif network_mode == "PUBLIC":
            runtime_option['iptable_rules'] = []
        elif network_mode == "PRIVATE":
            iptables = []
            # generate rdp port iptable
            ipt = genIPTablesRule(runtime_option['publicIP'], runtime_option['privateIP'], runtime_option['rdp_port'])
            iptables.append(ipt)

            # generate service port iptable
            if len(runtime_option['services_ports']) > 0:
                for sport in runtime_option['services_ports']:
                    ipt = genIPTablesRule(runtime_option['publicIP'], runtime_option['privateIP'], sport)
                    iptables.append(ipt)
            runtime_option['iptable_rules'] = iptables

    return runtime_option

def genIPTablesRule(fromip, toip, port):
    return {}

@login_required
def start_image_create_task(request, srcid):

    # create ectaskTransation Record
    _srcimgid        = srcid
    _dstimageid      = 'IMG' + genHexRandom()
    _instanceid      = 'TMPINS' + genHexRandom()
    _tid             = '%s:%s:%s' % (_srcimgid, _dstimageid, _instanceid )

    logger.error("tid=%s" % _tid)

    _ccip, _ccname = findLazyCC(srcid)
    _ncip = findLazyNC(_ccname)

    rec = ectaskTransaction(
         tid         = _tid,
         srcimgid    = _srcimgid,
         dstimgid    = _dstimageid,
         insid       = _instanceid,
         user        = request.user.username,
         phase       = 'preparing',
         vmstatus    = "",
         progress    = 0,
         ccip        = _ccip,
         ncip        = _ncip
    )
    rec.save()

    rec.runtime_option = json.dumps(genRuntimeOptionForImageBuild(_tid))
    rec.save()

    # open a window to monitor work progress
    imgobj = ecImages.objects.get(ecid = srcid)
    context = {
        'pagetitle' : "image create",
        'tid'       : _tid,
        'srcid'     : _srcimgid,
        'dstid'     : _dstimageid,
        "insid"     : _instanceid,
        'imgobj'    : imgobj,
        'steps'     : 0,
    }

    return render(request, 'clc/wizard/image_create_wizard.html', context)

def prepare_image_create_task(request, srcid, dstid, insid):
    _tid = "%s:%s:%s" % (srcid, dstid, insid)

    rec = ectaskTransaction.objects.get(tid=_tid)
    rec.phase = "preparing"
    rec.progress = 0
    rec.save()

    # # send request to CC to work
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/cc/api/1.0/image/create/task/prepare' % rec.ccip
    else:
        url = 'http://%s/cc/api/1.0/image/create/task/prepare' % rec.ccip
    payload = {
        'tid': _tid,
        'ncip': rec.ncip
    }
    r = requests.post(url, data=payload)
    logger.error(url + ":" + r.content)

    return HttpResponse(r.content, mimetype="application/json")

def run_image_create_task(request, srcid, dstid, insid):
    _tid = "%s:%s:%s" % (srcid, dstid, insid)

    rec = ectaskTransaction.objects.get(tid=_tid)
    rec.phase = "editing"
    rec.vmstatus = 'init'
    rec.save()

    # now everything is ready, start to run instance
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/cc/api/1.0/image/create/task/run' % rec.ccip
    else:
        url = 'http://%s/cc/api/1.0/image/create/task/run' % rec.ccip
    payload = {
        'tid'  : _tid,
        'ncip' : rec.ncip,
        'runtime_option' : rec.runtime_option,
    }
    r = requests.post(url, data=payload)
    return HttpResponse(r.content, mimetype="application/json")

def stop_image_create_task(request, srcid, dstid, insid):
    _tid = "%s:%s:%s" % (srcid, dstid, insid)
    rec = ectaskTransaction.objects.get(tid=_tid)
    rec.phase = "editing"
    rec.vmstatus = 'stopping'
    rec.save()

    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/cc/api/1.0/image/create/task/stop' % rec.ccip
    else:
        url = 'http://%s/cc/api/1.0/image/create/task/stop' % rec.ccip
    payload = {
        'tid': _tid,
        'ncip' : rec.ncip,
    }
    r = requests.post(url, data=payload)
    return HttpResponse(r.content, mimetype="application/json")

def image_create_task_getvmstatus(request, srcid, dstid, insid):
    pass

def submit_image_create_task(request, srcid, dstid, insid):
    _tid = "%s:%s:%s" % (srcid, dstid, insid)
    rec = ectaskTransaction.objects.get(tid=_tid)
    rec.phase = "submitting"
    rec.progress = 0

def image_create_task_getprogress(request, srcid, dstid, insid):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    tid = "%s:%s:%s" % (srcid, dstid, insid)
    try:
        payload = mc.get(str(tid))
        if payload == None:
            payload = {
                'type': 'taskstatus',
                'phase': "downloading",
                'progress': 0,
                'tid': tid,
                'failed' : False
            }
            response = json.dumps(payload)
        else:
            response = payload
            payload = json.loads(payload)
            if payload['progress'] < 0 :
                mc.delete(str(tid))
    except Exception as e:
        payload = {
            'type': 'taskstatus',
            'phase': "downloading",
            'progress': 0,
            'tid': tid,
            'failed' : False
        }
        response = json.dumps(payload)

    logger.error("lkf: get progress = %s", response)
    return HttpResponse(response, mimetype="application/json")

def image_modify_task(request, srcid):
    ccip = findLazyCC()

    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/cc/api/1.0/image/modify' % ccip
    else:
        url = 'http://%s/cc/api/1.0/image/modify' % ccip
    payload = {
        'ccname': getccnamebyconf()
    }
    r = requests.post(url, data=payload)
    return HttpResponse(r.content, mimetype="application/json")

def image_create_task_view(request,  srcid, dstid, insid):
    _tid = "%s:%s:%s" % (srcid, dstid, insid)
    _srcimgid        = srcid
    _dstimageid      = dstid
    _instanceid      = insid

    rec = ectaskTransaction.objects.get(tid=_tid)
    phase_array = ['preparing', 'editing', 'submitting']
    steps = phase_array.index(rec.phase)

    imgobj = ecImages.objects.get(ecid = srcid)
    context = {
        'pagetitle' : "image create",
        'tid'       : _tid,
        'srcid'     : _srcimgid,
        'dstid'     : _dstimageid,
        "insid"     : _instanceid,
        'imgobj'    : imgobj,
        'steps'     : steps,
    }

    return render(request, 'clc/wizard/image_create_wizard.html', context)



#################################################################################
# jTable views
#################################################################################

@login_required
def jtable_images(request):
    return render(request, 'clc/jtable/images_table.html', {})

@login_required
def jtable_tasks(request):
    return render(request, 'clc/jtable/tasks_table.html', {})

@login_required
def jtable_settings_for_authapth(request):
    return render(request, 'clc/jtable/authpath_table.html', {})

@login_required
def jtable_settings_for_ostypes(request):
    return render(request, 'clc/jtable/ostypes_table.html', {})

@login_required
def jtable_settings_for_rbac(request):
    return render(request, 'clc/jtable/rbac_table.html', {})

@login_required
def jtable_settings_for_vmusage(request):
    return render(request, 'clc/jtable/vmusage_table.html', {})

@login_required
def jtable_settings_for_serverrole(request):
    return render(request, 'clc/jtable/serverrole_table.html', {})

@login_required
def jtable_settings_for_vmtypes(request):
    return render(request, 'clc/jtable/vmtypes_table.html', {})

@login_required
def jtable_servers_cc(request):
    return render(request, 'clc/jtable/servers_cc_table.html', {})

@login_required
def jtable_servers_nc(request):
    return render(request, 'clc/jtable/servers_nc_table.html', {})

@login_required
def jtable_servers_lnc(request):
    return render(request, 'clc/jtable/servers_lnc_table.html', {})

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

def delete_authpath(request):
    response = {}

    rec = ecAuthPath.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_authpath(request):
    response = {}

    rec = ecAuthPath.objects.get(id=request.POST['id']);
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.ec_authpath_value = request.POST['ec_authpath_value']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

def delete_ostypes(request):
    response = {}
    data = []

    rec = ecOSTypes.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")


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
    return HttpResponse(retvalue, mimetype="application/json")

def delete_rbac(request):
    response = {}

    rec = ecRBAC.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

def delete_serverrole(request):
    response = {}

    rec = ecServerRole.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_serverrole(request):
    response = {}
    data = []

    rec = ecServerRole.objects.get(id=request.POST['id'])
    rec.ec_role_name = request.POST['ec_role_name']
    rec.ec_role_value = request.POST['ec_role_value']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")


def delete_vmtypes(request):
    response = {}

    rec = ecVMTypes.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_vmtypes(request):
    response = {}

    rec = ecVMTypes.objects.get(id=request.POST['id'])
    rec.name = request.POST['name']
    rec.memory = request.POST['memory']
    rec.cpus = request.POST['cpus']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

def delete_vmusage(request):
    response = {}

    rec = ecVMUsages.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_vmusage(request):
    response = {}

    rec = ecVMUsages.objects.get(id=request.POST['id'])
    rec.ec_usage = request.POST['ec_usage']

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")



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
            imgfile_size = os.path.getsize(imgfile_path)
            rec = ecImages(
                ecid = local_image,
                name = local_image,
                size = imgfile_size
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
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")


def delete_cc_resource(request):
    response = {}

    rec = ecCCResources.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

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
    return HttpResponse(retvalue, mimetype="application/json")

def create_cc_resource(request):
    pass

# core table functions for ecServers
def list_servers_by_role(reqeust, roletype):
    response = {}
    data = []

    recs = ecServers.objects.filter(role=roletype)
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['role'] = rec.role
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
        jrec['cpus'] = rec.cpus
        jrec['memory'] = rec.memory
        jrec['disk'] = rec.disk
        jrec['ccname'] = rec.ccname
        jrec['location'] = rec.location

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def list_servers(request):
    response = {}
    data = []

    recs = ecServers.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['role'] = rec.role
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
        jrec['cpus'] = rec.cpus
        jrec['memory'] = rec.memory
        jrec['disk'] = rec.disk
        jrec['ccname'] = rec.ccname
        jrec['location'] = rec.location

        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def delete_servers(request):
    response = {}

    rec = ecServers.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_servers(request):
    response = {}

    rec = ecServers.objects.get(id=request.POST['id'])
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.name = request.POST['name']
    rec.location = request.POST['location']

    rec.save()

    udate_cc_resource_available_resource(request.POST['id'])

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_servers(request):
    pass

# core tables for tasks
# ------------------------------------
def list_tasks(request):
    response = {}
    data = []

    recs = ectaskTransaction.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id']       = rec.id
        jrec['tid']      = rec.tid
        jrec['srcimgid'] = rec.srcimgid
        jrec['dstimgid'] = rec.dstimgid
        jrec['insid']    = rec.insid
        jrec['user']     = rec.user
        jrec['phase']    = rec.phase
        jrec['vmstatus'] = rec.vmstatus
        jrec['completed']= rec.completed
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


def delete_tasks(request):
    response = {}

    rec = ectaskTransaction.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


# core tables for images
# ------------------------------------
def list_images(request):
    autoFindNewAddImage()

    response = {}
    data = []

    recs = ecImages.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['ecid'] = rec.ecid
        jrec['name'] = rec.name
        jrec['ostype']=rec.ostype
        jrec['usage'] = rec.usage
        jrec['description'] = rec.description
        jrec['version'] = rec.version
        jrec['size'] = rec.size
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


def delete_images(request):
    response = {}

    rec = ecImages.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_images(request):
    response = {}

    rec = ecImages.objects.get(id=request.POST['id'])
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.name = request.POST['name']
    rec.ostype = request.POST['ostype']
    rec.usage = request.POST['usage']
    rec.description = request.POST['description']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_images(request):
    response = {}
    data = []

    rec = ecImages(
        ec_authpath_name = request.POST['ec_authpath_name'],
        ecid = request.POST['ecid'],
        name = request.POST['name'],
        ostype = request.POST['ostype'],
        usage = request.POST['usage'],
        description = request.POST['description'],
        version = request.POST['version'],
        size = request.POST['size'],
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_authpath_name'] = rec.ec_authpath_name
    jrec['ecid'] = rec.ecid
    jrec['name'] = rec.name
    jrec['ostype']=rec.ostype
    jrec['usage'] = rec.usage
    jrec['description'] = rec.description
    jrec['version'] = rec.version
    jrec['size'] = rec.size
    data.append(jrec)

    response['Result'] = 'OK'
    response['Record'] = data

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

#################################################################################
# API Version 1.0 for image build & modify
#################################################################################
def register_host(request):
    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def list_ncs(request):
    ncs = ecServers.objects.filter(role='nc', ccname=request.POST['ccname'])
    ncsips = []
    for nc in ncs:
        ncsips.append(nc.ip0)

    response = {}
    response['Result'] = 'OK'
    response['ncs'] = ncsips
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def register_server(request):
    response = {}

    if request.POST['role'] == 'clc' or request.POST['role'] == 'walrus':
        try:
            rec = ecServers.objects.get(role=request.POST['role'])
            rec.role   = request.POST['role']
            rec.name   = request.POST['name']
            rec.cpus   = request.POST['cpus']
            rec.memory = request.POST['memory']
            rec.disk   = request.POST['disk']
            rec.ip0    = request.POST['ip0']
            rec.ip1    = request.POST['ip1']
            rec.ip2    = request.POST['ip2']
            rec.ip3    = request.POST['ip3']
            rec.mac0   = request.POST['mac0']
            rec.mac1   = request.POST['mac1']
            rec.mac2   = request.POST['mac2']
            rec.mac3   = request.POST['mac3']
            logger.error("update existing server db")
        except:
            rec = ecServers(
                role   = request.POST['role'],
                name   = request.POST['name'],
                cpus   = request.POST['cpus'],
                memory = request.POST['memory'],
                disk   = request.POST['disk'],
                ip0    = request.POST['ip0'],
                ip1    = request.POST['ip1'],
                ip2    = request.POST['ip2'],
                ip3    = request.POST['ip3'],
                mac0   = request.POST['mac0'],
                mac1   = request.POST['mac1'],
                mac2   = request.POST['mac2'],
                mac3   = request.POST['mac3'],
            )
            logger.error("create a new server db")
        rec.save()
    else:
        try:
            rec = ecServers.objects.get(role=request.POST['role'],
                                        ip0=request.POST['ip0'])
            rec.role   = request.POST['role']
            rec.name   = request.POST['name']
            rec.cpus   = request.POST['cpus']
            rec.memory = request.POST['memory']
            rec.disk   = request.POST['disk']
            rec.ip0    = request.POST['ip0']
            rec.ip1    = request.POST['ip1']
            rec.ip2    = request.POST['ip2']
            rec.ip3    = request.POST['ip3']
            rec.mac0   = request.POST['mac0']
            rec.mac1   = request.POST['mac1']
            rec.mac2   = request.POST['mac2']
            rec.mac3   = request.POST['mac3']
            rec.ccname = request.POST['ccname']
        except:
            rec = ecServers(
                    role   = request.POST['role'],
                    name   = request.POST['name'],
                    cpus   = request.POST['cpus'],
                    memory = request.POST['memory'],
                    disk   = request.POST['disk'],
                    ip0    = request.POST['ip0'],
                    ip1    = request.POST['ip1'],
                    ip2    = request.POST['ip2'],
                    ip3    = request.POST['ip3'],
                    mac0   = request.POST['mac0'],
                    mac1   = request.POST['mac1'],
                    mac2   = request.POST['mac2'],
                    mac3   = request.POST['mac3'],
                    ccname = request.POST['ccname'],
                )
        rec.save()

        if request.POST['role'] == 'cc':
            try:
                ccresource = ecCCResources.objects.get(ccip=request.POST['ip0'], ccname=request.POST['ccname'])
                pass
            except:
                rec = ecCCResources(
                    ccip        = request.POST['ip0'],
                    ccname      = request.POST['ccname'],
                    usage       = "lvd",
                    network_mode= '',
                    portRange   = "3389-4389",
                )
                rec.save()

    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

#################################################################################
# some common APIs
#################################################################################
def get_walrus_info(request):
    rec = ecServers.objects.get(role='walrus')
    payload = {
        'role':   rec.role,
        'name':   rec.name,
        'cpus':   rec.cpus,
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
    return HttpResponse(retvalue, mimetype="application/json")

def get_image_info(imgid):
    rec = ecImages.objects.get(ecid=imgid)
    payload = {
        'ecid':     rec.ecid,
        'name':     rec.name,
        'ostype':   rec.ostype,
        'usage':    rec.usage,
        'description': rec.description,
        'version':     rec.version,
        'size':        rec.size
    }
    response = {}
    response['Result'] = "OK"
    response['data'] = payload
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")
