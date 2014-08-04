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
    return render(request, 'clc/index.html', {})

