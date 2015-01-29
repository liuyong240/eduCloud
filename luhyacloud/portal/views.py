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
    context = {
    }
    return render(request, 'portal/cloud-services.html', context)

@login_required
def portal_vds(request):
    context = {
    }
    return render(request, 'portal/cloud-desktop.html', context)