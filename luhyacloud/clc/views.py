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

from clc.models import *
from clc import tasks
from luhyaapi import *

MAX_LOGFILE_BYTE=10*1024*1024
LOG_FILE='/var/log/eucalyptus/clc.log/'
MAX_LOG_COUNT=10

# Get an instance of a logger
logger = logging.getLogger(__name__)

def display_login_window(request):
    return render(request, 'clc/login.html', {})

def user_login(request):
    response = {}
    username = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            response['status'] = "SUCCESS"
            response['url'] = "/clc/index"
            return HttpResponse(json.dumps(response), mimetype='application/json')
        else:
            # Return a 'disabled account' error message
            response['status'] = "FAILURE"
            response['reason'] = "account is disabled"
            return HttpResponse(json.dumps(response), mimetype='application/json')
    else:
        # Return an 'invalid login' error message.
        response['status'] = "FAILURE"
        response['reason'] = "account is invalid"
        return HttpResponse(json.dumps(response), mimetype='application/json')

def user_logout(request):
    logout(request)
    return render(request, 'clc/login.html', {})

@login_required
def index_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "System Run-time Status Overview",
    }
    return render(request, 'clc/overview.html', context)

@login_required
def accounts_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Account Management",
    }
    return render(request, 'clc/accounts.html', context)

@login_required
def images_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Images Management",
    }

    return render(request, 'clc/images.html', context)

@login_required
def hosts_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Hosts Management",
    }
    return render(request, 'clc/hosts.html', context)

@login_required
def settings_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "System Settings Management",
    }
    return render(request, 'clc/settings.html', context)

@login_required
def vss_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Cloud App Management",
    }

    return render(request, 'clc/vss.html', context)

@login_required
def rvds_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Remote Cloud Desktop Management",
    }

    return render(request, 'clc/rvds.html', context)

@login_required
def lvds_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Local Cloud Desktop Management",
    }

    return render(request, 'clc/lvds.html', context)

@login_required
def tasks_view(request):
    context = {
        'loginname': request.user,
        'dashboard' : "Tasks Management",
    }

    return render(request, 'clc/tasks.html', context)


@login_required
def jtable_images(request):
    return render(request, 'clc/jtable/images_table.html', {})

# API Version 1.0
def list_images(request):
    response = {}
    data = []

    recs = ecImages.objects.all()
    for rec in recs:
        jrec = {}
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['ecid'] = rec.ecid
        jrec['name'] = rec.name
        jrec['ostype']=rec.ostype
        jrec['usage'] = rec.usage
        jrec['description'] = rec.description
        jrec['publish_date'] = str(rec.publish_date)
        jrec['version'] = rec.version
        jrec['size'] = rec.size
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


def delete_images(request):
    pass

def update_images(request):
    pass

def create_images(request):
    response = {}
    rec = ecImages(
        ec_authpath_name = request.POST['ec_authpath_name'],
        ecid = request.POST['ecid'],
        name = request.POST['name'],
        ostype = request.POST['ostype'],
        usage = request.POST['usage'],
        description = request.POST['description'],
        publish_date = request.POST['publish_date'],
        version = request.POST['version'],
        size = request.POST['size'],
    )
    rec.save()

    response['Result'] = 'OK'
    response['Records'] = rec

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")
