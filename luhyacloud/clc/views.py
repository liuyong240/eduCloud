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



#################################################################################
# jTable views
#################################################################################

@login_required
def jtable_images(request):
    return render(request, 'clc/jtable/images_table.html', {})

@login_required
def jtable_settings(request):
    return render(request, 'clc/jtable/authpath_table.html', {})






#################################################################################
# API Version 1.0 for accessing data model by POST request
#################################################################################

# settings tables ecAuthPath
# -----------------------------------
def list_authpath(request):
    response = {}
    data = []

    recs = ecAuthPath.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['ec_authpath_value'] = rec.ec_authpath_value
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def delete_authpath(request):
    response = {}

    rec = ecAuthPath.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_authpath(request):
    response = {}

    rec = ecAuthPath.objects.get(id=request.POST['id']);
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.ec_authpath_value = request.POST['ec_authpath_value']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_authpath(request):
    response = {}
    data = []

    rec = ecAuthPath(
        ec_authpath_name = request.POST['ec_authpath_name'],
        ec_authpath_value = request.POST['ec_authpath_value']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_authpath_name'] = rec.ec_authpath_name
    jrec['ec_authpath_value'] = rec.ec_authpath_value
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

# settings tables ecAuthPath
# -----------------------------------
def list_ostypes(request):
    response = {}
    data = []

    recs = ecOSTypes.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_ostype'] = rec.ec_ostype
        jrec['ec_storagectl'] = rec.ec_storagectl
        jrec['ec_waishe_para'] = rec.ec_waishe_para
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def delete_ostypes(request):
    response = {}
    data = []

    rec = ecOSTypes.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_ostypes(request):
    response = {}

    rec = ecOSTypes.objects.get(id=request.POST['id']);
    rec.ec_ostype = request.POST['ec_ostype']
    rec.ec_storagectl = request.POST['ec_storagectl']
    rec.ec_waishe_para = request.POST['ec_waishe_para']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_ostypes(request):
    response = {}
    data = []

    rec = ecOSTypes(
        ec_ostype = request.POST['ec_ostype'],
        ec_storagectl = request.POST['ec_storagectl'],
        ec_waishe_para = request.POST['ec_waishe_para']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_ostype'] = rec.ec_ostype
    jrec['ec_storagectl'] = rec.ec_storagectl
    jrec['ec_waishe_para'] = rec.ec_waishe_para
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


# settings tables ecRBAC
# -----------------------------------
def list_rbac(request):
    response = {}
    data = []

    recs = ecRBAC.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['ec_rbac_name'] = rec.ec_rbac_name
        jrec['ec_rbac_permision'] = rec.ec_rbac_permision
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def delete_rbac(request):
    response = {}

    rec = ecRBAC.objects.all(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_rbac(request):
    response = {}
    data = []

    rec = ecRBAC.objects.all(id=request.POST['id'])
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.ec_rbac_name = request.POST['ec_rbac_name']
    rec.ec_rbac_permision = request.POST['ec_rbac_permision']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_rbac(request):
    response = {}
    data = []

    rec= ecRBAC(
        ec_authpath_name = request.POST['ec_authpath_name'],
        ec_rbac_name = request.POST['ec_rbac_name'],
        ec_rbac_permision = request.POST['ec_rbac_permision']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_authpath_name'] = rec.ec_authpath_name
    jrec['ec_rbac_name'] = rec.ec_rbac_name
    jrec['ec_rbac_permision'] = rec.ec_rbac_permision
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

# settings tables ecAuthPath
# -----------------------------------
def list_serverrole(request):
    response = {}
    data = []

    recs = ecServerRole.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_role_name'] = rec.ec_role_name
        jrec['ec_role_value'] = rec.ec_role_value
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def delete_serverrole(request):
    response = {}

    rec = ecServerRole.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_serverrole(request):
    response = {}
    data = []

    rec = ecServerRole.objects.get(id=request.POST['id'])
    rec.ec_role_name = request.POST['ec_role_name']
    rec.ec_role_value = request.POST['ec_role_value']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_serverrole(request):
    response = {}
    data = []

    rec = ecServerRole (
        ec_role_name = request.POST['ec_role_name'],
        ec_role_value = request.POST['ec_role_value']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_role_name'] = rec.ec_role_name
    jrec['ec_role_value'] = rec.ec_role_value
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

# settings tables ecVMTypes
# -----------------------------------
def list_vmtypes(request):
    response = {}
    data = []

    recs = ecVMTypes.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['name'] = rec.name
        jrec['memory'] = rec.memory
        jrec['cpus'] = rec.cpus
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def delete_vmtypes(request):
    response = {}

    rec = ecVMTypes.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_vmtypes(request):
    response = {}

    rec = ecVMTypes.objects.get(id=request.POST['id'])
    rec.name = request.POST['name']
    rec.memory = request.POST['memory']
    rec.cpus = request.POST['cpus']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_vmtypes(request):
    response = {}
    data = []

    rec = ecVMTypes(
        name = request.POST['name'],
        memory = request.POST['memory'],
        cpus = request.POST['cpus']
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['name'] = rec.name
    jrec['memory'] = rec.memory
    jrec['cpus'] = rec.cpus
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

# settings tables ecVMUsage
# -----------------------------------
def list_vmusage(request):
    response = {}
    data = []

    recs = ecVMUsages.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_usage'] = rec.ec_usage
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def delete_vmusage(request):
    response = {}

    rec = ecVMUsages.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_vmusage(request):
    response = {}

    rec = ecVMUsages.objects.get(id=request.POST['id'])
    rec.ec_usage = request.POST['ec_usage']

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_vmusage(request):
    response = {}
    data = []

    rec = ecVMUsages(
        ec_usage = request.POST['ec_usage'],
    )
    rec.save()

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_usage'] = rec.ec_usage
    data.append(jrec)

    response['Record'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


# core tables for images
# ------------------------------------
def list_images(request):
    response = {}
    data = []

    recs = ecImages.objects.all()
    for rec in recs:
        jrec = {}
        jrec['id'] = rec.id
        jrec['ec_authpath_name'] = rec.ec_authpath_name
        jrec['ecid'] = rec.ecid
        jrec['name'] = rec.name
        jrec['ostype']=rec.ostype
        jrec['usage'] = rec.usage
        jrec['description'] = rec.description
        jrec['version'] = rec.version
        jrec['size'] = rec.size
        data.append(jrec)

    response['Records'] = data
    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")


def delete_images(request):
    response = {}

    rec = ecImages.objects.get(id=request.POST['id'])
    rec.delete()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def update_images(request):
    response = {}

    rec = ecImages.objects.get(id=request.POST['id'])
    rec.ec_authpath_name = request.POST['ec_authpath_name']
    rec.ecid = request.POST['ecid']
    rec.name = request.POST['name']
    rec.ostype = request.POST['ostype']
    rec.usage = request.POST['usage']
    rec.description = request.POST['description']
    rec.version = request.POST['version']
    rec.size = request.POST['size']
    rec.save()

    response['Result'] = 'OK'

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")

def create_images(request):
    response = {}
    data = []

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

    jrec = {}
    jrec['id'] = rec.id
    jrec['ec_authpath_name'] = rec.ec_authpath_name
    jrec['ecid'] = rec.ecid
    jrec['name'] = rec.name
    jrec['ostype']=rec.ostype
    jrec['usage'] = rec.usage
    jrec['description'] = rec.description
    jrec['version'] = rec.version
    jrec['size'] = rec.size
    data.append(jrec)

    response['Result'] = 'OK'
    response['Record'] = data

    retvalue = json.dumps(response)
    return HttpResponse(retvalue, mimetype="application/json")



