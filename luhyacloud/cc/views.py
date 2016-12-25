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
from luhyaapi.hostTools import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.clcAPIWrapper import *
from luhyaapi.zmqWrapper import *


logger = getcclogger()

# Create your views here.
#################################################################################
# API Version 1.0 for image build & modify
#################################################################################
import requests, memcache

def AddIPtableRule(ipt):
    # first need to check these iptables is already configured or not
    pass

def RemoveIPtableRule(ipt):
    pass

def removeIPtables_image_create_task(request):
    logger.error("--- --- --- removeIPtables_image_create_task")

    runtime_option = json.loads(request.POST['runtime_option'])
    if len(runtime_option['iptable_rules']) > 0:
        for ipt in runtime_option['iptable_rules']:
            RemoveIPtableRule(ipt)

    # return http response
    response = {}
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


#####################################
## Image build functions
#####################################
def image_create_task_prepare(request):
    logger.error("--- --- --- prepare_image_create_task")
    ncip = request.POST['ncip']

    message = {}
    message['type']             = "cmd"
    message['op']               = 'image/prepare'
    message['tid']              = request.POST['tid']
    message['runtime_option']   = request.POST['runtime_option']
    message = json.dumps(message)

    zmq_send(ncip, message, NC_CMD_QUEUE_PORT)
    logger.error("--- --- ---zmq: send prepare cmd to nc sucessfully")

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def image_create_task_run(request):
    logger.error("--- --- --- run_image_create_task")

    ncip = request.POST['ncip']

    message = {}
    message['type']             = "cmd"
    message['op']               = 'image/run'
    message['tid']              = request.POST['tid']
    message['runtime_option']   = request.POST['runtime_option']

    _message = json.dumps(message)
    zmq_send(ncip, _message, NC_CMD_QUEUE_PORT)
    logger.error("--- --- ---zmq: send run cmd to nc sucessfully")

    # check for runtime_option for cc's side work
    runtime_option = json.loads(message['runtime_option'])
    if len(runtime_option['iptable_rules']) > 0:
        for ipt in runtime_option['iptable_rules']:
            AddIPtableRule(ipt)

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def image_create_task_stop(request):
    logger.error("--- --- --- stop_image_create_task")

    ncip = request.POST['ncip']

    message = {}
    message['type']             = "cmd"
    message['op']               = 'image/stop'
    message['tid']              = request.POST['tid']
    message['runtime_option']   = request.POST['runtime_option']

    _message = json.dumps(message)
    zmq_send(ncip, _message, NC_CMD_QUEUE_PORT)
    logger.error("--- --- ---zmq: send stop cmd to nc sucessfully")

    # check for runtime_option for cc's side work
    runtime_option = json.loads(message['runtime_option'])
    if len(runtime_option['iptable_rules']) > 0:
        for ipt in runtime_option['iptable_rules']:
            RemoveIPtableRule(ipt)

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def image_create_task_submit(request):
    logger.error("--- --- --- submit_image_create_task")

    ncip = request.POST['ncip']

    message = {}
    message['type']             = "cmd"
    message['op']               = 'image/submit'
    message['tid']              = request.POST['tid']
    message['runtime_option']   = request.POST['runtime_option']
    message = json.dumps(message)

    zmq_send(ncip, message, NC_CMD_QUEUE_PORT)
    logger.error("--- --- ---zmq: send submit cmd to nc sucessfully")

    # return http response
    response = {}
    response['Result'] = 'OK'
    response['tid'] = request.POST['tid']

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def register_lnc(request):
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/register/lnc' % clcip
    else:
        url = 'http://%s/clc/api/1.0/register/lnc' % clcip
    payload = {
        'ip':       request.POST['ip'],
        'mac':     request.POST['mac'],

        'name':     request.POST['name'],
        'ccname':   request.POST['ccname'],
        'location': request.POST['location'],

        'cores':    request.POST['cores'],
        'memory':   request.POST['memory'],
        'disk':     request.POST['disk'],
        'runtime_option': request.POST['runtime_option']
    }
    r = requests.post(url, data=payload)
    return HttpResponse(r.content, content_type="application/json")

# def register_terminal(request):
#     clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
#     if DAEMON_DEBUG == True:
#         url = 'http://%s:8000/clc/api/1.0/register/tnc' % clcip
#     else:
#         url = 'http://%s/clc/api/1.0/register/tnc' % clcip
#     payload = {
#         'ip':       request.POST['ip'],
#         'mac':     request.POST['mac'],
#
#         'name':     request.POST['name'],
#         'osname':   request.POST['osname'],
#         'location': request.POST['location'],
#
#         'cores':    request.POST['cores'],
#         'memory':   request.POST['memory'],
#         'disk':     request.POST['disk'],
#     }
#     r = requests.post(url, data=payload)
#     return HttpResponse(r.content, content_type="application/json")

def register_server(request):
    logger.error('call register_server in cc ... ... ')
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)

    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/register/server' % clcip
    else:
        url = 'http://%s/clc/api/1.0/register/server' % clcip
    payload = {
        'role':     request.POST['role'],
        'name':     request.POST['name'],
        'cores':     request.POST['cores'],
        'memory':   request.POST['memory'],
        'disk':     request.POST['disk'],
        'exip':     request.POST['exip'],
        'ip0':      request.POST['ip0'],
        'ip1':      request.POST['ip1'],
        'ip2':      request.POST['ip2'],
        'ip3':      request.POST['ip3'],
        'mac0':     request.POST['mac0'],
        'mac1':     request.POST['mac1'],
        'mac2':     request.POST['mac2'],
        'mac3':     request.POST['mac3'],
        'ccname':   request.POST['ccname'],
        'hypervisor': request.POST['hypervisor'],
    }
    logger.error('call register_server in clc ... ... ')
    r = requests.post(url, data=payload)

    return HttpResponse(r.content, content_type="application/json")

def get_images_version(request):
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

def verify_clc_cc_file_ver(request):
    tid = request.POST['tid']
    imgid = tid.split(':')[0]
    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)

    clc_img_info = getImageInfo(clcip, tid)
    cc_img_info  = getImageVersionFromCC('127.0.0.1', tid)

    response = {}
    response['Result']  = "OK"
    response['clc']     = clc_img_info['data']
    response['cc']      = cc_img_info['data']
    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def delete_tasks(request):
    tid = request.POST['tid']

    logger.error("--- --- --- cc delete_tasks %s" % tid)

    ncip = request.POST['ncip']

    message = {}
    message['type']             = "cmd"
    message['op']               = 'task/delete'
    message['tid']              = tid
    message['runtime_option']   = request.POST['runtime_option']
    message = json.dumps(message)

    zmq_send(ncip, message, NC_CMD_QUEUE_PORT)
    logger.error("--- --- ---zmq: send task delete cmd to nc sucessfully")

    # return http response
    response = {}
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")