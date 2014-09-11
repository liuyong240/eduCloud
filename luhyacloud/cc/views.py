# coding=UTF-8

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

def prepare_image_create_task(request):

    message = {}
    message['type'] = "cmd"
    message['op']   = 'image/prepare'
    message['paras']= request.POST['tid']
    message = json.dumps(message)

    routing_send(logger, 'localhost', 'nc_cmd', message, request.POST['ncip'])

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def setupIPtableRules(ipt):
    pass

def run_image_create_task(request):
    ncip = request.POST['ncip']

    message = {}
    message['type'] = "cmd"
    message['op']   = 'image/run'
    message['paras']= request.POST['tid']
    message['runtime_option'] = request.POST['runtime_option']
    message = json.dumps(message)

    routing_send(logger, 'localhost', 'nc_cmd', message, ncip)

    # check for runtime_option for cc's side work
    runtime_option = json.loads(message['runtime_option'])
    if len(runtime_option['iptable_rules']) > 0:
        for ipt in runtime_option['iptable_rules']:
            setupIPtableRules(ipt)

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


def stop_image_create_task(request):
    ncip = request.POST['ncip']

    message = {}
    message['type'] = "cmd"
    message['op']   = 'image/stop'
    message['paras']= request.POST['tid']
    message = json.dumps(message)

    routing_send(logger, 'localhost', 'nc_cmd', message, ncip)

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def submit_image_create_task(request):
    ncip = request.POST['ncip']

    message = {}
    message['type'] = "cmd"
    message['op']   = 'image/submit'
    message['paras']= request.POST['tid']
    message = json.dumps(message)

    routing_send(logger, 'localhost', 'nc_cmd', message, ncip)

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def register_host(request):
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)

    url = 'http://%s/clc/api/1.0/register/host' % clcip
    payload = {

    }
    r = requests.post(url, data=payload)
    return HttpResponse(r.content, mimetype="application/json")

def register_server(request):
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)

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
