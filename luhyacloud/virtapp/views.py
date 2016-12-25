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

from clc.models import *
from models import *

from luhyaapi.educloudLog import *
from luhyaapi.hostTools import *
from luhyaapi.settings import *
from sortedcontainers import SortedList
import requests, memcache
from django.utils.translation import ugettext as _

from luhyaapi.adToolWrapper import *

logger = getclclogger()

# Create your views here.
@login_required(login_url='/portal/admlogin')
def ldaps_setting(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    ldaps_para = ldapsPara.objects.filter()
    if ldaps_para.count() > 0:
        rec = ldaps_para[0]
    else:
        rec = None

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("LDAPS Settings"),
        'role'      : ua_role_value.ec_authpath_value,
        'para'      : rec,
    }
    return render(request, 'virtapp/ldaps_settings.html', context)

@login_required(login_url='/portal/admlogin')
def vapp_mgr(request):
    u = User.objects.get(username=request.user)
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'uid':   u.username,
        'showname': ua.showname,
        'dashboard' : _("VAPP Management"),
        'role'      : ua_role_value.ec_authpath_value,
    }
    return render(request, 'virtapp/vapp_mgr.html', context)

def set_ldaps_para(request):
    ldaps_para = ldapsPara.objects.filter()
    if ldaps_para.count() > 0:
        rec = ldaps_para[0]
        rec.uri         = request.POST['uri']
        rec.binddn      = request.POST['binddn']
        rec.bindpw      = request.POST['password']
        rec.searchbase  = request.POST['searchbase']
        rec.domain      = request.POST['domain']

        rec.save()
    else:
        rec = ldapsPara(
            uri         = request.POST['uri'],
            binddn      = request.POST['binddn'],
            bindpw      = request.POST['password'],
            searchbase  = request.POST['searchbase'],
            domain      = request.POST['domain']
        )

        rec.save()

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def usercreate(request):
    ldaps_para = ldapsPara.objects.filter()
    basedn = 'cn=Users,%s' % ldaps_para[0].searchbase
    adobj = adWrappper(ldaps_para[0].uri, ldaps_para[0].binddn, ldaps_para[0].bindpw, basedn)

    if adobj.connect() == True:
        if adobj.isUserExist(request.POST['username']):
            adobj.SetPass(request.POST['username'], request.POST['password'], basedn)
        else:
            adobj.AddUser(request.POST['username'], request.POST['password'], basedn, ldaps_para[0].domain)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def setpass(request):
    ldaps_para = ldapsPara.objects.filter()
    basedn = 'cn=Users,%s' % ldaps_para[0].searchbase
    adobj = adWrappper(ldaps_para[0].uri, ldaps_para[0].binddn, ldaps_para[0].bindpw, basedn)

    if adobj.connect() == True:
        if adobj.isUserExist(request.POST['username']):
            adobj.SetPass(request.POST['username'],  request.POST['password'], basedn)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def userdelete(request):
    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def userupdate(request):
    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def jtable_vapps(request):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    context = {
        'role':  ua_role_value.ec_authpath_value,
    }
    return render(request, 'virtapp/jtable/vapp_table.html', context)

def list_vapp(request):
    response = {}
    data = []

    recs = virtApp.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id']              = rec.id
        jrec['uuid']            = rec.uuid
        jrec['app_display_name']= rec.app_display_name
        jrec['app_remote_name'] = rec.app_remote_name
        jrec['app_exe_path']    = rec.app_exe_path
        jrec['ecids']           = rec.ecids
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_vapp(request):
    response = {}

    rec = virtApp.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def vapp_add(request):
    context = {
    }
    return render(request, 'virtapp/form/new_vapp.html', context)

def create_vapp(request):
    rec = virtApp(
        uuid=       genHexRandom(),
        app_display_name=    request.POST['vapp_display_name'],
        app_remote_name =    request.POST['vapp_remote_name'],
        app_exe_path=        request.POST['vapp_exe_path'],
        ecids=               request.POST['vapp_ecids'],
    )
    rec.save()

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def vapp_edit(request, appid):
    rec = virtApp.objects.get(uuid=appid)
    context = {
        'vappobj': rec,
    }
    return render(request, 'virtapp/form/edit_vapp.html', context)

def edit_vapp(request):
    rec = virtApp.objects.get(uuid=request.POST['vapp_uuid'])
    rec.app_display_name    = request.POST['vapp_display_name']
    rec.app_remote_name     = request.POST['vapp_remote_name']
    rec.app_exe_path        = request.POST['vapp_exe_path']
    rec.ecids               = request.POST['vapp_ecids']
    rec.save()

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def vapp_perm_edit(request, appid):
    ua = ecAccount.objects.get(userid=request.user)
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)
    if ua_role_value.ec_authpath_value != 'eduCloud.admin':
        context = {
            'pagetitle'     : _('Error Report'),
            'error'         : _('Only eduCloud.Admin can change vapp permission!'),
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

    rec = virtApp.objects.get(uuid=appid)
    permsObjs = vapp_auth.objects.filter(uuid=rec.uuid)
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
        'res'   :  rec.app_display_name,
        'id'    :  rec.uuid,
        'roles' :  roles,
         'lists':  range(0,rows),
        'next'  :   rows,
        'perms' :  perms,
    }

    return render(request, 'virtapp/form/permission.html', context)

def vapp_perm_update(id, data):
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
                rec = vapp_auth.objects.get(uuid=id, role_value= _role)
                rec.read    = _read
                rec.write   = _write
                rec.execute = _execute
                rec.create  = _create
                rec.delete  = _delete
                rec.save()
            except:
                rec = vapp_auth(
                    uuid        = id,
                    role_value  = _role,
                    read        = _read,
                    write       = _write,
                    execute     = _execute,
                    create      = _create,
                    delete      = _delete,
                )
                rec.save()

def update_perm(request):
    id = request.POST['id']
    data = request.POST['data']

    vapp_perm_update(id, data)

    response = {}
    response['Result'] = "OK"
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def list_my_vapps(request):
    index = 0
    available_vapps = []
    # get current user's role
    ua = ecAccount.objects.get(userid=request.POST['uid'])
    ua_role_value = ecAuthPath.objects.get(ec_authpath_name = ua.ec_authpath_name)

    vo_auths = vapp_auth.objects.filter(role_value=ua_role_value.ec_authpath_value)
    for vo_auth in vo_auths:
        vo = virtApp.objects.get(uuid=vo_auth.uuid)
        vap = {}
        vap['uuid']     = vo.uuid
        vap['name']     = vo.app_display_name
        vap['id']       = 'myapp' + str(index)
        available_vapps.append(vap)
        index = index + 1

    response = {}
    response['Result'] = "OK"
    response['data']   = available_vapps
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def run_vapp(request):
    logger.error(" 1111111 ")
    user_id = request.POST['uid']
    app_uuid = request.POST['uuid']

    logger.error(" 22222222 ")
    # get domain user
    recs = ldapsPara.objects.filter()
    domain = recs[0].domain
    domain_user = "%s\%s" % (domain, user_id)

    logger.error(" 33333333 ")
    # get vapp path & running instance
    vapp_obj = virtApp.objects.get(uuid=app_uuid)
    logger.error("user %s will try to run vapp:%s" % ( domain_user, vapp_obj.app_remote_name))

    # looking for instance that runs this vapp
    ecids = vapp_obj.ecids
    imgids = ecids.split(',')
    l = SortedList()
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    logger.error(" 44444444 ")
    for imgid in imgids:
        if len(imgid) > 0:
            imgid = imgid.strip()
            trecs = ectaskTransaction.objects.filter(srcimgid = imgid, dstimgid = imgid)
            if trecs.count() > 0:
                # collect all live instance, and sort
                for trec in trecs:
                    vm = {}
                    ncobj = ecServers.objects.get(ip0 = trec.ncip, role='nc')
                    key = str("nc#" + ncobj.mac0 + "#status")
                    try:
                        payload = mc.get(key)
                        if payload == None:
                            continue
                        else:
                            payload = json.loads(payload)
                            if 'vm_data' in payload.keys():
                                _vminfo = payload['vm_data']
                                for _vm in _vminfo:
                                    if _vm['insid'] == trec.insid and _vm['state'] == 'Running':
                                        vm['1cpu'] = _vm['phy_cpu']
                                        vm['2mem'] = _vm['phy_mem']
                                        vm['insid'] = trec.insid
                                        l.add(vm)
                                    else:
                                        continue
                            else:
                                continue
                    except Exception as e:
                        continue

    response = {}
    if len(l) > 0:
        logger.error(l)
        rec = ectaskTransaction.objects.get(insid = l[0]['insid'])
        runtime_options = json.loads(rec.runtime_option)
        logger.error(" --- find instace %s for vapp %s " % (runtime_options['web_ip'], vapp_obj.app_remote_name))

        vapp_info = {}
        vapp_info['ip']         =  runtime_options['web_ip']
        vapp_info['user']       =  user_id
        vapp_info['domain']     =  domain
        vapp_info['displayname']=  vapp_obj.app_display_name
        vapp_info['remoteapp']  =  vapp_obj.app_remote_name
        vapp_info['exepath']    =  vapp_obj.app_exe_path

        response['Result'] = "OK"
        response['data']  =  vapp_info
    else:
        response['Result'] = "FAIL"
        response['error'] = 'Not Find running instances with app %s' % vapp_obj.app_remote_name


    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")








