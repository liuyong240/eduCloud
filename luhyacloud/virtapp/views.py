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
from luhyaapi.luhyaTools import configuration
from luhyaapi.hostTools import *
from luhyaapi.settings import *
from sortedcontainers import SortedList
import requests, memcache
from django.utils.translation import ugettext as _

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

def updateLDAPSConf():
    ldaps_para = ldapsPara.objects.filter()
    URI  = "URI %s\n" % ldaps_para[0].uri
    uri  = "uri %s\n" % ldaps_para[0].uri
    BASE = "BASE %s\n" % ldaps_para[0].searchbase
    TLS  = "TLS_REQCERT allow\n"
    binddn = "binddn %s\n" % ldaps_para[0].binddn
    bindpw = "bindpw %s\n" % ldaps_para[0].bindpw
    searchbase = "searchbase %s\n" % ldaps_para[0].searchbase

    # update /etc/ldap/ldap.conf
    filepath = "/tmp/ldap.conf"
    text_file = open (filepath, "w")
    text_file.writelines(BASE)
    text_file.writelines(URI)
    text_file.writelines(TLS)
    text_file.close()
    cmd = "sudo mv /tmp/ldap.conf /etc/ldap/ldap.conf"
    commands.getoutput(cmd)

    # update /etc/adtool.cfg
    filepath = "/tmp/adtool.cfg"
    text_file = open (filepath, "w")
    text_file.writelines(uri)
    text_file.writelines(binddn)
    text_file.writelines(bindpw)
    text_file.writelines(searchbase)
    text_file.close()
    cmd = "sudo mv /tmp/adtool.cfg /etc/adtool.cfg"
    commands.getoutput(cmd)

def set_ldaps_para(request):
    ldaps_para = ldapsPara.objects.filter()
    if ldaps_para.count() > 0:
        rec = ldaps_para[0]
        rec.uri         = request.POST['uri']
        rec.binddn      = request.POST['binddn']
        rec.bindpw      = request.POST['password']
        rec.searchbase  = request.POST['searchbase']

        rec.save()
    else:
        rec = ldapsPara(
            uri         = request.POST['uri'],
            binddn      = request.POST['binddn'],
            bindpw      = request.POST['password'],
            searchbase  = request.POST['searchbase'],
        )

        rec.save()

    updateLDAPSConf()

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def usercreate(request):
    ldaps_para = ldapsPara.objects.filter()
    group = 'cn=Users,%s' % ldaps_para[0].searchbase

    cmd = 'adtool usercreate %s %s' % (request.POST['username'], group)
    output = commands.getoutput(cmd)
    logger.error("%s \n %s" % (cmd, output))
    cmd = 'adtool setpass %s %s' % (request.POST['username'], request.POST['password'])
    output = commands.getoutput(cmd)
    logger.error("%s \n %s" % (cmd, output))
    output = cmd = 'adtool userunlock %s' % request.POST['username']
    output = commands.getoutput(cmd)
    logger.error("%s \n %s" % (cmd, output))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def userdelete(request):
    cmd = 'adtool userdelete %s' % request.POST['username']
    output = commands.getoutput(cmd)
    logger.error("%s \n %s" % (cmd, output))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def userupdate(request):
    group = 'cn=Users,%s' % ldaps_para[0].searchbase
    cmd = 'adtool list %s' % group
    output = commands.getoutput(cmd)
    logger.error("%s \n %s" % (cmd, output))


    is_en_vapp = request.POST['vapp_en']
    if is_en_vapp == 'yes':
        cmd = 'adtool userunlock %s' % request.POST['username']
    else:
        cmd = 'adtool userlock %s' % request.POST['username']
    output = commands.getoutput(cmd)
    logger.error("%s \n %s" % (cmd, output))

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def setpass(request):
    cmd = 'adtool setpass %s %s' % (request.POST['username'], request.POST['password'])
    output = commands.getoutput(cmd)
    logger.error("%s \n %s" % (cmd, output))

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
        jrec['id']      = rec.id
        jrec['uuid']    = rec.uuid
        jrec['appname'] = rec.appname
        jrec['apppath'] = rec.apppath
        jrec['ecids']   = rec.ecids
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
        appname=    request.POST['vapp_name'],
        apppath=    request.POST['vapp_path'],
        ecids=      request.POST['vapp_ecids'],
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
    rec.appname = request.POST['vapp_name']
    rec.apppath = request.POST['vapp_path']
    rec.ecids   = request.POST['vapp_ecids']
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
        'res'   : rec.appname,
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
        vap['name']     = vo.appname
        vap['path']     = vo.apppath
        vap['id']       = 'myapp' + str(index)
        available_vapps.append(vap)
        index = index + 1

    response = {}
    response['Result'] = "OK"
    response['data']   = available_vapps
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def run_vapp(request):
    bFindInstance = False

    vapp_obj = virtApp.objects.get(uuid=request.POST['uuid'])
    cmdline = 'rdesktop -A "c:\Program Files\ThinLinc\WTSTools\seamlessrdpshell.exe" -s "%s" %s -u "%s"'

    # looking for instance that runs this vapp
    ecids = vapp_obj.ecids
    imgids = ecids.split(',')
    for imgid in imgids:
        imgid = imgid.strip()
        insts = ecVSS.objects.filter(imageid=imgid)
        for inst in insts:
            trec = ectaskTransaction.objects.filter(insid = inst)
            phase = trec.phase
            state = trec.state
            if phase == 'editing':
                if state == 'Running' or state == 'running':
                    runtime_options = json.loads(trec.runtime_option)
                    cmdline = cmdline % (vapp_obj.apppath, runtime_options['web_ip'], request.POST['uid'])
                    bFindInstance = True
                    break

    response = {}
    if bFindInstance:
        response['Result'] = "OK"
        response['cmdline'] = cmdline
    else:
        response['Result'] = "FAIL"
        response['error'] = 'Not Find running instances'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")






