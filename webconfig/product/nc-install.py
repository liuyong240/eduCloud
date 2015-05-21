import os, commands, sys
import time

DST_IP = '192.168.56.103'

def checkPackage( pname ):
    cmd_line = 'dpkg -l | grep %s' % pname
    output = commands.getoutput(cmd_line)
    if len(output) > 0 and output.split()[0] == 'ii':
       return True
    else:
       return False

##############################################################################
# 1. update /etc/apt/sources.list
##############################################################################
if not os.path.exists('/etc/apt/sources.list.luhya'):
    cmd_line = 'sudo cp /etc/apt/sources.list /etc/apt/sources.list.luhya'
    commands.getoutput(cmd_line)

    cmd_line = 'cp /etc/apt/sources.list /tmp/'
    commands.getoutput(cmd_line)

    with open('/tmp/sources.list', 'a') as myfile:
        myfile.write('\ndeb http://%s/debian/ zhejiang non-free' % DST_IP)

    cmd_line = 'sudo cp /tmp/sources.list /etc/apt/sources.list'
    commands.getoutput(cmd_line)

##############################################################################
# 2. Import the repository's public key
##############################################################################
cmd_line = 'apt-key list | grep luhya'
ret = commands.getoutput(cmd_line)
if ret == '':
    cmd_line = 'curl http://%s/packages.educloud.key > /tmp/packages.educloud.key' % DST_IP
    commands.getoutput(cmd_line)
    cmd_line = 'sudo apt-key add /tmp/packages.educloud.key'
    commands.getoutput(cmd_line)

##############################################################################
# 3. Fetch the list of packages available at the new source
##############################################################################
cmd_line = 'sudo rm /var/lib/apt/lists/*'
os.system(cmd_line)
cmd_line = 'sudo rm /var/lib/apt/lists/partial/*'
os.system(cmd_line)
cmd_line = 'sudo apt-get update'
os.system(cmd_line)

##############################################################################
# 5. create a user named luhya
##############################################################################
cmd_line = 'sudo cut -d: -f1 /etc/passwd | grep luhya'
ret = commands.getoutput(cmd_line)
if ret == '':
    cmd_line = 'sudo useradd  -m -s /bin/bash -U luhya'
    commands.getoutput(cmd_line)

##############################################################################
# 6. create /storage directories and download data.vdi
##############################################################################
if not os.path.exists('/var/log/educloud'):
    os.system('sudo mkdir -p /var/log/educloud')
if not os.path.exists('/storage'):
    os.system('sudo mkdir /storage')
if not os.path.exists('/storage/images'):
    os.system('sudo mkdir -p /storage/images')
    os.system('sudo mkdir -p /storage/VMs')
    os.system('sudo mkdir -p /storage/config')
    os.system('sudo mkdir -p /storage/space')
if not os.path.exists('/storage/tmp'):
    os.system('sudo mkdir -p /storage/tmp')
if not os.path.exists('/storage/tmp/images'):
    os.system('sudo mkdir -p /storage/tmp/images')
    os.system('sudo mkdir -p /storage/tmp/VMs')

##############################################################################
# 7. install educloud in one machine by apt-get
##############################################################################
cmd_line = 'sudo apt-get -y install nodedaemon-nc'
os.system(cmd_line)

cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
os.system(cmd_line)

if checkPackage('nodedaemon-nc') == False:
   print "--------------------------------------------------"
   print "Install nodedaemon-nc Failed, please try again."
   print "--------------------------------------------------"
   exit(1)

# install vbox ext pack
cmd_line = 'wget http://%s/Oracle_VM_VirtualBox_Extension_Pack-4.3.20-96996.vbox-extpack' % DST_IP
os.system(cmd_line)

cmd_line = 'sudo vboxmanage extpack install Oracle_VM_VirtualBox_Extension_Pack-4.3.20-96996.vbox-extpack'
os.system(cmd_line)

cmd_line = 'rm Oracle_VM_VirtualBox_Extension_Pack-4.3.20-96996.vbox-extpack'
os.system(cmd_line)

##############################################################################
# 8. install 3rd python and rsync lib
##############################################################################
cmd_line = 'wget http://%s/pip.tar' % DST_IP
os.system(cmd_line)
cmd_line = 'tar vxf pip.tar -C /tmp/'
commands.getoutput(cmd_line)
cmd_line = 'rm /tmp/Django*.tar.gz /tmp/MySQL*.tar.gz /tmp/python-memcached*.tar.gz /tmp/amqp*.tar.gz'
os.system(cmd_line)
cmd_line = 'sudo pip install /tmp/*.tar.gz'
os.system(cmd_line)
cmd_line = 'sudo dpkg -i /tmp/*.deb'
os.system(cmd_line)
cmd_line = 'rm pip.tar'
commands.getoutput(cmd_line)

#######################################
# 12 configure  cc.conf
#######################################
if checkPackage('nodedaemon-cc') == False:
    ccname = raw_input("Enter Cluster Name: ")
    ccnamestr = "ccname=%s" % ccname
    ccip   = raw_input("Enter Cluster IP  : ")
    ccipstr =  "IP=%s\n" % ccip

    with open('/storage/config/cc.conf', 'w') as myfile:
        myfile.write('[server]\n')
        ccipstr =  "IP=%s\n" % ccip
        myfile.write(ccipstr)
        myfile.write(ccnamestr)

    ##############################################################################
    # 13. configure sshfs
    ##############################################################################
    cmd_line = 'sudo -u luhya ssh-keygen'
    os.system(cmd_line)
    cmd_line = 'ssh-copy-id ' + ccip
    os.system(cmd_line)

cmd_line = 'sudo chown -R luhya:luhya /storage/config'
commands.getoutput(cmd_line)

##############################################################################
# 14. clear download packages
##############################################################################
cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
commands.getoutput(cmd_line)
cmd_line = 'sudo rm /var/cache/apt/archives/partial/*.deb'
commands.getoutput(cmd_line)

print '----------------------------------------------------------'
print  'Now system will reboot to enable node daemon ... ... ...'
time.sleep(1)
print '... ... ... ... ...'
cmd_line = 'sudo reboot'
commands.getoutput(cmd_line)