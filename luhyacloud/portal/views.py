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
from luhyaapi.hostTools import *
from luhyaapi.settings import *
from sortedcontainers import SortedList
import requests, memcache
from django.utils.translation import ugettext as _

logger = getclclogger()

def portal_home(request):
    context = {
    }
    return render(request, 'portal/index.html', context)

def portal_login(request):
    context = {
    }
    return render(request, 'portal/login.html', context)

def portal_adm_login(request):
    context = {
    }
    return render(request, 'portal/adm_login.html', context)

def portal_ppts(request):
    context = {
    }
    return render(request, 'portal/ppts.html', context)

def portal_videos(request):
    context = {
    }
    return render(request, 'portal/videos.html', context)

def portal_sdk(request):
    context = {
    }
    return render(request, 'portal/sdk.html', context)

def portal_documents(request):
    context = {
    }
    return render(request, 'portal/documents.html', context)

def portal_vapp(request):
    clcip = getclcipbyconf()
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/list_sites' % clcip
    else:
        url = 'http://%s/clc/api/1.0/list_sites' % clcip

    r = requests.get(url)
    result = json.loads(r.content)

    context = {
        'sites': result['data']
    }
    return render(request, 'portal/cloud-services.html', context)

@login_required(login_url='/portal/vdlogin')
def portal_vds(request):
    logger.error("enter portal_vds")
    clcip = getclcipbyconf()
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/list_myvds' % clcip
    else:
        url = 'http://%s/clc/api/1.0/list_myvds' % clcip

    payload = {
        'user': request.user.username,
        'sid':  request.session.session_key,
    }

    try:
        r = requests.post(url, data=payload)
        result = json.loads(r.content)
        context = {
            'uid': request.user.username,
            'vds': result['data'],
            'vapps': result['vapp'],
            'sid': request.session.session_key,
        }
    except Exception as e:
        logger.error("portal_vds call list_myvds with exception = %s" % str(e))
        context = {
            'uid': request.user.username,
            'vds': [],
            'vapps': [],
            'sid': request.session.session_key,
        }

    return render(request, 'portal/cloud-desktop.html', context)

def user_logout(request):
    logout(request)
    return render(request, 'portal/login.html', {})