# coding=UTF-8

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

import json
from celery.result import AsyncResult
import random, pickle, pexpect, os, base64, shutil, time, datetime
import logging
import commands
from datetime import datetime

from luhyaapi.educloudLog import *
from luhyaapi.luhyaTools import configuration
from luhyaapi.hostTools import *
from luhyaapi.rabbitmqWrapper import *


logger = getcclogger()

# Create your views here.
#################################################################################
# API Version 1.0 for image build & modify
#################################################################################
import requests, memcache

def findLazyNC():
    clcip = getclcipbyconf()
    url = 'http://%s/clc/api/1.0/list/ncs' % clcip
    payload = {
        'ccname': getccnamebyconf()
    }
    r = requests.post(url, data=payload)
    return json.loads(r.content)['ncs'][0]

def image_build(request, srcid, destid):
    # send cmd to nc which are consuming the cmd_queue
    message = {}
    paras = " %s %s " % (srcid, destid)
    message['type'] = "cmd"
    message['op']   = 'imagebuild'
    message['paras']= paras
    message = json.dumps(message)

    routing_send(logger, 'localhost', 'cc_cmd', message, findLazyNC())

    # return http response
    response = {}
    response['Result'] = 'OK'
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def register_host(request):
    clcip = getclcipbyconf()

    url = 'http://%s/clc/api/1.0/register/host' % clcip
    payload = {

    }
    r = requests.post(url, data=payload)
    return HttpResponse(r.content, mimetype="application/json")

def register_server(request):
    clcip = getclcipbyconf()

    url = 'http://%s/clc/api/1.0/register/server' % clcip
    payload = {
        'role':     request.POST['role'],
        'name':     request.POST['name'],
        'cpus':     request.POST['cpus'],
        'memory':   request.POST['memory'],
        'disk':     request.POST['disk'],
        'ip0':      request.POST['ip0'],
        'ip1':      request.POST['ip1'],
        'ip2':      request.POST['ip2'],
        'ip3':      request.POST['ip3'],
        'mac0':     request.POST['mac0'],
        'mac1':     request.POST['mac1'],
        'mac2':     request.POST['mac2'],
        'mac3':     request.POST['mac3'],
        'ccname':   request.POST['ccname'],
    }
    r = requests.post(url, data=payload)
    return HttpResponse(r.content, mimetype="application/json")