from django.db import models
from django.forms import ModelForm

# Create your models here.

#==============================================
# Basic setting for system
#==============================================

class ecAuthPath(models.Model):
    ec_authpath_name = models.CharField(max_length=100)
    ec_authpath_value = models.CharField(max_length=100)

# namely, group definition
class ecRBAC(models.Model):
    ec_authpath_name = models.CharField(max_length=100)
    ec_rbac_name = models.CharField(max_length=20)

    # None, {read | write | execute | create | delete }, Full
    # 1 or 0 represent enable/disable at different position
    # None: 000000
    # Read+Write   110000
    # Read+Execute 101000
    # Read+Create+Delete 100110
    # full   000001 or xxxxx1
    ec_rbac_permision = models.CharField(max_length=6)

# possible values for imgfile_ostype are :
# Windows:  Windows XP, Windows 7, Windows 2003, Windows 2008, Windows 2012
# Linux:    Ubuntu, Ubuntu_64
# ostype already include 32/64bit information
class ecOSTypes(models.Model):
    # possible values for imgfile_ostype are :
    # Windows:  Windows XP, Windows 7, Windows 2003, Windows 2008, Windows 2012
    # Linux:    Ubuntu, Ubuntu_64
    # ostype already include 32/64bit information
    ec_ostype = models.CharField(max_length=20)
    ec_storagectl = models.CharField(max_length=100)
    ec_waishe_para = models.CharField(max_length=100)

# currently only 2 value: Server and Desktop
class ecVMUsages(models.Model):
    ec_usage = models.CharField(max_length=20)

# currently 5 values: clc, walrus, cc, nc, sc
class ecServerRole(models.Model):
    ec_role_name = models.CharField(max_length=100)
    ec_role_value = models.CharField(max_length=10)

class ecVMTypes(models.Model):
    # available value are as below
    # and can be modified or added by amin:

    # for VSS default:
    # vssmall:  m=4G, cpu=1
    # vsmedium: m=8G, cpu=1
    # vslarge:  m=16G,cpu=1

    # for VDS default,
    # vdsmall:  m=1G, cpu=1
    # vdmedium  m=4G, cpu=1
    # vdlarge   m=4G, cpu=1
    # vdxlarege m=4G, cpu=2
    name = models.CharField(max_length=20)
    memory = models.IntegerField(default=1)
    cpus = models.IntegerField(default=1)

#==============================================
# Core table definition
#==============================================
class ecServers(models.Model):
    ec_authpath_name = models.CharField(max_length=100)

    # an array of roles' value, should be json string
    role = models.CharField(max_length=100)

    ip0 = models.CharField(max_length=20)
    ip1 = models.CharField(max_length=20)
    ip2 = models.CharField(max_length=20)
    ip3 = models.CharField(max_length=20)

    # used for remote LAN-awake, or WAN-awake.
    mac0 = models.CharField(max_length=20)
    mac1 = models.CharField(max_length=20)
    mac2 = models.CharField(max_length=20)
    mac3 = models.CharField(max_length=20)

    name = models.CharField(max_length=20)
    location = models.CharField(max_length=20)

    cpus = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    disk = models.IntegerField(default=0)

    ccname = models.CharField(max_length=20)

class ecHosts(models.Model):
    ec_authpath_name = models.CharField(max_length=100)

    ip  = models.CharField(max_length=20)
    wip = models.CharField(max_length=20)

    # used for remote LAN-awake, or WAN-awake.
    mac = models.CharField(max_length=20);

    name = models.CharField(max_length=20)
    ccname = models.CharField(max_length=20)
    location = models.CharField(max_length=20)

    cpus = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    disk = models.IntegerField(default=0)

    # value as json formate, display value by a function
    runtime_option = models.TextField()

class ecImages(models.Model):
    ec_authpath_name = models.CharField(max_length=100)

    ecid = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20)

    ostype = models.CharField(max_length=20)

    # possible value are : desktop, server
    usage = models.CharField(max_length=20)

    description = models.TextField()
    version = models.CharField(max_length=10)
    size = models.DecimalField(max_digits=8,decimal_places=2)

class ecVAPP(models.Model):
    ec_authpath_name = models.CharField(max_length=100)


class ecVSS(models.Model):
    ec_authpath_name = models.CharField(max_length=100)

    ecid = models.CharField(max_length=10, unique=True)
    imageid = models.CharField(max_length=10)
    name = models.CharField(max_length=20)

    vmtypename = models.CharField(max_length=20)

    # host server(IP or any), access mode/para,  persistent/temperary,
    # network(manage IP, access IP, internal IP, etc)
    # rdp port
    # should be a json string
    runtime_option = models.TextField()

    description = models.TextField()

class ecVDS(models.Model):
    ec_authpath_name = models.CharField(max_length=100)

    ecid = models.CharField(max_length=10, unique=True)
    imageid = models.CharField(max_length=10)
    name = models.CharField(max_length=20)

    vmtypename = models.CharField(max_length=20)
    # host server(IP or any), access mode/para,  persistent/temperary,
    # network(manage IP, access IP, internal IP, etc)
    # should be a json string
    runtime_option = models.TextField()

    description = models.TextField()

#==============================================
# Run-time table definition
#==============================================
class taskTransaction(models.Model):
    tid         = models.CharField(max_length=100, unique=True)
    srcimgid    = models.CharField(max_length=20)
    dstimgid    = models.CharField(max_length=20)
    insid       = models.CharField(max_length=20)
    user        = models.CharField(max_length=100)
    phase       = models.CharField(max_length=100)
    progress    = models.IntegerField(default=0)
    accessURL   = models.CharField(max_length=100)
    ccip        = models.CharField(max_length=100)
    ncip        = models.CharField(max_length=100)
    message     = models.TextField()
    completed   = models.BooleanField(default=False)

# class ecImageBuildTask(models.Model):
#     # /tmp/ImageBuildTask/type/oldid/newid/id
#     type=models.CharField(max_length=10) #{new_build, modify_build}
#     oldimgid=models.CharField(max_length=10)
#     newimgid=models.CharField(max_length=10, unique=True)
#     status=models.CharField(max_length=50) #{cloned, pending, running}
#     walrusip=models.GenericIPAddressField()
#     ccip=models.GenericIPAddressField()
#     ncip=models.GenericIPAddressField()
#     acurl=models.CharField(max_length=100)
#
# class ecImageSyncTask(models.Model):
#     destip=models.GenericIPAddressField()
#     destid=models.CharField(max_length=10)
#     srcfile=models.TextField()
#     destfile=models.TextField()
#     status=models.CharField(max_length=10)
