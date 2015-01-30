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

@login_required
def portal_vds(request):
    clcip = getclcipbyconf()
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/list_sites' % clcip
    else:
        url = 'http://%s/clc/api/1.0/list_sites' % clcip

    r = requests.get(url)
    result = json.loads(r.content)

    context = {
        'uid' : request.user.username,
        'tvds' : result['data'],
    }
    return render(request, 'portal/cloud-desktop.html', context)