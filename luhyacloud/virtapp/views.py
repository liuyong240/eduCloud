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

    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")
