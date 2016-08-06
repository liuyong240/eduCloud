# coding=UTF-8

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist



import json
import commands
from datetime import datetime

from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *

logger = getclclogger()

# Create your views here.
#################################################################################
# API Version 1.0 for image build & modify
#################################################################################
import requests, memcache


def machine_cpu_util(request):
    response = {}
    response['value'] = getSysCpuUtil()
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")


def machine_mem_util(request):
    response = {}
    response['value'] = getSysMemUtil()
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def machine_net_util(request):
    response = {}
    response['value'] = getSysNetworkUtil()
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def machine_disk_util(request):
    response = {}
    response['value'] = getSysDiskUtil()
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, content_type="application/json")

def get_service_status(request):
    logger.error("get_service_status start --- --- ")
    role = request.POST['role']
    result = getServiceStatus(role )
    retvalue = json.dumps(result)
    return HttpResponse(retvalue, content_type="application/json")

def get_hardware_status(request):
    result = getHostHardware()
    retvalue = json.dumps(result)
    return HttpResponse(retvalue, content_type="application/json")
