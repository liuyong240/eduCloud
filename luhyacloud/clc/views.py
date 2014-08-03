# coding=UTF-8

from django.shortcuts import render
from django.http import HttpResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from clc.models import *
from django.core.exceptions import ObjectDoesNotExist
from clc import tasks
from celery.result import AsyncResult
import random, pickle, pexpect, os, base64, shutil, time, datetime
import logging
import commands
from luhyaapi import *
from datetime import datetime

MAX_LOGFILE_BYTE=10*1024*1024
LOG_FILE='/var/log/eucalyptus/clc.log/'
MAX_LOG_COUNT=10

# Get an instance of a logger
logger = logging.getLogger(__name__)

def logon_view(request):
    return render(request, 'clc/login.html', {})
