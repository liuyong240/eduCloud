from django.db import models
from django.forms import ModelForm

# Create your models here.

#==============================================
# Basic setting for system
#==============================================

# mysql> describe auth_user;
# +--------------+--------------+------+-----+---------+----------------+
# | Field        | Type         | Null | Key | Default | Extra          |
# +--------------+--------------+------+-----+---------+----------------+
# | id           | int(11)      | NO   | PRI | NULL    | auto_increment |
# | password     | varchar(128) | NO   |     | NULL    |                |
# | last_login   | datetime     | NO   |     | NULL    |                |
# | is_superuser | tinyint(1)   | NO   |     | NULL    |                |
# | username     | varchar(30)  | NO   | UNI | NULL    |                |
# | first_name   | varchar(30)  | NO   |     | NULL    |                |
# | last_name    | varchar(30)  | NO   |     | NULL    |                |
# | email        | varchar(75)  | NO   |     | NULL    |                |
# | is_staff     | tinyint(1)   | NO   |     | NULL    |                |
# | is_active    | tinyint(1)   | NO   |     | NULL    |                |
# | date_joined  | datetime     | NO   |     | NULL    |                |
# +--------------+--------------+------+-----+---------+----------------+
class ecAccount(models.Model):
    userid              = models.CharField(max_length=30)
    showname            = models.CharField(max_length=30)
    ec_authpath_name    = models.CharField(max_length=100)
    phone               = models.CharField(max_length=30)
    description         = models.TextField()
    vdpara              = models.TextField()

# Auth Rule for ecAccount DB
# - a.b.admin can manage all account with auth_name looks like a.b.*
# - a.b.admin can get full control on all resource a.b.*

class ecAuthPath(models.Model):
    ec_authpath_name = models.CharField(max_length=100)
    ec_authpath_value = models.CharField(max_length=100)

# namely, group definition
class ecRBAC(models.Model):
    ec_authpath_name = models.CharField(max_length=100)
    ec_rbac_name = models.CharField(max_length=100)

    # None, {read | write | execute | create | delete }, Full
    # 1 or 0 represent enable/disable at different position
    # None: 000000
    # Read+Write   110000
    # Read+Execute 101000
    # Read+Create+Delete 100110
    # full   000001 or xxxxx1
    ec_rbac_permision = models.CharField(max_length=10)

# possible values for imgfile_ostype are :
# Windows:  Windows XP, Windows 7, Windows 2003, Windows 2008, Windows 2012
# Linux:    Ubuntu, Ubuntu_64
# ostype already include 32/64bit information
class ecOSTypes(models.Model):
    # possible values for imgfile_ostype are :
    # Windows:  Windows XP, Windows 7, Windows 2003, Windows 2008, Windows 2012
    # Linux:    Ubuntu, Ubuntu_64
    # ostype already include 32/64bit information
    ec_ostype      = models.CharField(max_length=20)
    ec_disk_type   = models.CharField(max_length=100)
    ec_nic_type    = models.CharField(max_length=100)
    ec_audio_para  = models.CharField(max_length=100)

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
    name = models.CharField(max_length=100)
    memory = models.IntegerField(default=1)
    cpus = models.IntegerField(default=1)

#==============================================
# Core table definition
#==============================================
class ecServers(models.Model):

    # an array of roles' value, should be json string
    role = models.CharField(max_length=100)

    ip0 = models.CharField(max_length=20)
    ip1 = models.CharField(max_length=20)
    ip2 = models.CharField(max_length=20)
    ip3 = models.CharField(max_length=20)
    eip = models.CharField(max_length=20)

    # used for remote LAN-awake, or WAN-awake.
    mac0 = models.CharField(max_length=20)
    mac1 = models.CharField(max_length=20)
    mac2 = models.CharField(max_length=20)
    mac3 = models.CharField(max_length=20)

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    cpu_cores = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    disk = models.IntegerField(default=0)

    ccname = models.CharField(max_length=100)

class ecServers_auth(models.Model):
    mac0        = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)

class ecClusterNetMode(models.Model):
    network_mode   = models.CharField(max_length=20)

class ecCCResources(models.Model):
    ccip           = models.CharField(max_length=20)
    ccname         = models.CharField(max_length=100)
    usage          = models.CharField(max_length=20) #lvd, rvd, vss, app
    network_mode   = models.CharField(max_length=20) # manual, public, private

    portRange      = models.CharField(max_length=100) # port1-port2
    publicIPRange  = models.CharField(max_length=100) # ip1-ip2
    privateIPRange = models.CharField(max_length=100) # ip1-ip2
    service_ports  = models.CharField(max_length=100) # [80,21, 8080, 22]

    available_rdp_ports        = models.TextField()  # [port1, port2, port3, ... ... ]
    used_rdp_ports             = models.TextField()  # [port1, port2, ports, ... ... ]
    available_ips_macs         = models.TextField()  # [{pubip1, prvip1, mac1}, {pubip2, prvip2, mac2},{pubip3, prvip3, mac3}, ... ... ]
    used_ips_macs              = models.TextField()  # [{pubip1, prvip1, mac1}, {pubip2, prvip2, mac2},{pubip3, prvip3, mac3}, ... ... ]

# for all NCs that support LVD
class ecHosts(models.Model):
    ip  = models.CharField(max_length=20)
    wip = models.CharField(max_length=20)

    # used for remote LAN-awake, or WAN-awake.
    mac = models.CharField(max_length=20);

    name = models.CharField(max_length=100)
    ccname = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    cpus = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    disk = models.IntegerField(default=0)

    # auto_sync = 1,
    # auto_poweroff=1
    # offline_enabled=1
    # is_pad=0
    # auto_guest_attr_update=0
    runtime_option = models.TextField()

class ecHosts_auth(models.Model):
    mac0        = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)

#
# Images
#
class ecImages(models.Model):
    ecid = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    ostype = models.CharField(max_length=20)

    # possible value are : desktop, server
    usage = models.CharField(max_length=20)

    description = models.TextField()
    version = models.CharField(max_length=10)
    size = models.IntegerField(default=0)

class ecImages_auth(models.Model):
    ecid        = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)

#
# Instance and VMs
#
class ecVAPP(models.Model):
    appid = models.CharField(max_length=20, unique=True)

class ecVAPP_auth(models.Model):
    appid       = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)


class ecVSS(models.Model):
    insid       = models.CharField(max_length=20, unique=True)
    imageid     = models.CharField(max_length=20)
    name        = models.CharField(max_length=100)
    description = models.TextField()

    creator     = models.CharField(max_length=100)
    run_user    = models.CharField(max_length=100)

    phase       = models.CharField(max_length=100)
    vmstatus    = models.CharField(max_length=100) # init, running, stopped(default)
    progress    = models.IntegerField(default=0)   # 0(default)-100, -100, <0
    message     = models.TextField()

    user_accessURL  = models.CharField(max_length=500)
    mgr_accessURL   = models.CharField(max_length=500)

    defined_ccname = models.CharField(max_length=100)
    defined_ncip   = models.CharField(max_length=100)
    runtime_ccname = models.CharField(max_length=100)
    runtime_ncip   = models.CharField(max_length=100)

    # network(public IP, private IP, MAC port, etc)
    # hardware para(cpus, memory, disktype, nictype, audio_para)
    # iptable forward rule( )
    # fullscreen = 1, minitoolbar = 0 auto_unregister
    runtime_option = models.TextField()

class ecVSS_auth(models.Model):
    insid       = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)

class ecVDS(models.Model):
    insid       = models.CharField(max_length=20, unique=True)
    imageid     = models.CharField(max_length=20)
    name        = models.CharField(max_length=100)
    description = models.TextField()

    creator     = models.CharField(max_length=100)
    run_user    = models.CharField(max_length=100)

    phase       = models.CharField(max_length=100)
    vmstatus    = models.CharField(max_length=100) # init, running, stopped(default)
    progress    = models.IntegerField(default=0)   # 0(default)-100, -100, <0
    message     = models.TextField()

    accessURL   = models.CharField(max_length=500)

    defined_ccname = models.CharField(max_length=100)
    defined_ncip   = models.CharField(max_length=100)
    runtime_ccname = models.CharField(max_length=100)
    runtime_ncip   = models.CharField(max_length=100)

    # access mode/para,  persistent/temperary,
    # network(public IP, private IP, MAC port, etc)
    # hardware para(cpus, memory, disktype, nictype, audio_para)
    # iptable forward rule( )
    # fullscreen = 1, minitoolbar = 0 auto_unregister
    runtime_option = models.TextField()

class ecVDS_auth(models.Model):
    insid       = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)


class ecLVDS(models.Model):
    insid       = models.CharField(max_length=20, unique=True)

class ecLVDS_auth(models.Model):
    insid       = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)


#==============================================
# Run-time table definition
#==============================================
class ectaskTransaction(models.Model):
    tid         = models.CharField(max_length=100, unique=True)

    srcimgid    = models.CharField(max_length=20)
    dstimgid    = models.CharField(max_length=20)
    insid       = models.CharField(max_length=20)
    user        = models.CharField(max_length=100)
    phase       = models.CharField(max_length=100)
    vmstatus    = models.CharField(max_length=100) # init, running, stopped(default)
    progress    = models.IntegerField(default=0)   # 0(default)-100, -100, <0
    accessURL   = models.CharField(max_length=500)
    ccip        = models.CharField(max_length=100)
    ncip        = models.CharField(max_length=100)
    runtime_option = models.TextField()
    message     = models.TextField()
    completed   = models.BooleanField(default=False)

class ectaskTransactionauth(models.Model):
    tid         = models.CharField(max_length=100, unique=True)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)
    fullctl     = models.BooleanField(default=False)

