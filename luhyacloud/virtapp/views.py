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
    URI  = "URI %s" % ldaps_para[0].uri
    uri  = "uri %s" % ldaps_para[0].uri
    BASE = "BASE %s" % ldaps_para[0].searchbase
    TLS  = "TLS_REQCERT allow"
    binddn = "binddn %s" % ldaps_para[0].binddn
    bindpw = "bindpw %s" % ldaps_para[0].bindpw
    searchbase = "searchbase %s" % ldaps_para[0].searchbase

    # update /etc/ldap/ldap.conf
    filepath = "/tmp/ldap.conf/"
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
    text_file.writelines(base)
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
    group = 'cn=Users,' % ldaps_para[0].searchbase

    cmd = 'adtool usercreate %s %s' % (request.POST['username'], group)
    commands.getoutput(cmd)
    cmd = 'adtool setpass %s %s' % (request.POST['username'], request.POST['password'])
    commands.getoutput(cmd)
    cmd = 'adtool userunlock %s' % request.POST['username']
    commands.getoutput(cmd)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def userdelete(request):
    cmd = 'adtool userdelete %s' % request.POST['username']
    commands.getoutput(cmd)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def userupdate(request):
    is_en_vapp = request.POST['vapp_en']
    if is_en_vapp == 'yes':
        cmd = 'adtool userunlock %s' % request.POST['username']
    else:
        cmd = 'adtool userlock %s' % request.POST['username']
    commands.getoutput(cmd)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def setpass(request):
    cmd = 'adtool setpass %s %s' % (request.POST['username'], request.POST['password'])
    commands.getoutput(cmd)

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")
