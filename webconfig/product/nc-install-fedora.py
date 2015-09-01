import os, commands, sys
import time

def checkPackage( pname ):
    cmd_line = 'rpm -qa | grep %s' % pname
    output = commands.getoutput(cmd_line)
    if len(output) > 0 and output.split()[0] == 'ii':
       return True
    else:
       return False

##############################################################################
# 1. get the repository server IP
##############################################################################
if len(sys.argv) > 1:
    DST_IP = sys.argv[1]
else:
    DST_IP = '121.41.80.147'


##############################################################################
# 5. create a user named luhya
##############################################################################
cmd_line = 'sudo cut -d: -f1 /etc/passwd | grep luhya'
ret = commands.getoutput(cmd_line)
if ret == '':
    print "--------------------------------------------------"
    print " Add a new user luhya.                            "
    cmd_line = 'sudo useradd  -m -d /home/luhya -s /bin/bash -U luhya'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo usermod --password $(echo luhya | openssl passwd -1 -stdin) luhya'
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
if not os.path.exists('/usr/local/nodedaemon'):
    os.system('sudo mkdir -p /usr/local/nodedaemon/nc/')

cmd_line = 'sudo chown -R luhya:luhya /storage && sudo chmod -R 777 /storage'
commands.getoutput(cmd_line)

cmd_line = 'sudo chown -R luhya:luhya /usr/local/nodedaemon && sudo chmod -R 777 /usr/local/nodedaemon'
commands.getoutput(cmd_line)

cmd_line = 'sudo chown -R luhya:luhya /var/log/educloud'
commands.getoutput(cmd_line)

##############################################################################
# the content of fedora nc installation include
# 8   - copy nc_daemon binary file to /usr/local/nodedaemon/nc/
cmd_line = 'wget http://%s/fedora/nc_daemon' % DST_IP
os.system(cmd_line)
cmd_line = 'mv nc_daemon /usr/local/nodedaemon/nc/'
os.system(cmd_line)

# 9   - install modified rsync.rpm
cmd_line = 'wget http://%s/fedora/rsync-3.1.1-6.fc22.x86_64.rpm' % DST_IP
os.system(cmd_line)
cmd_line = 'sudo rpm -i --reinstall rsync-3.1.1-6.fc22.x86_64.rpm'
os.system(cmd_line)

# 10   - install necessary python package
# cmd_line = 'wget http://%s/pip.tar' % DST_IP
# os.system(cmd_line)
# cmd_line = 'tar vxf pip.tar -C /tmp/'
# commands.getoutput(cmd_line)
# cmd_line = 'sudo pip install /tmp/netifaces-*.tar.gz /tmp/psutil-*.tar.gz /tmp/linux-metrics-*.tar.gz /tmp/sorted*.tar.gz /tmp/pkia-*.tar.gz /tmp/pexpect-*.tar.gz'
# os.system(cmd_line)
# cmd_line = 'rm pip.tar'
# commands.getoutput(cmd_line)

# 11   - install necessary rpm package
cmd_line = 'sudo dnf -y install sshfs'
os.system(cmd_line)
# Pre-requisites
# grep ' vmx svm ' /proc/cpuinfo
cmd_line = 'sudo dnf -y groupinstall "Virtualization" '
os.system(cmd_line)


# 12. add auto start service script for nodedaemon-nc
cmd_line = 'wget http://%s/fedora/nodedaemon-nc.service' % DST_IP
os.system(cmd_line)
cmd_line = 'sudo mv nodedaemon-nc.service /lib/systemd/system/'
os.system(cmd_line)
cmd_line = 'sudo ln -s /lib/systemd/system/nodedaemon-nc.service /etc/systemd/system/multi-user.target.wants/nodedaemon-nc.service'
os.system(cmd_line)
cmd_line = 'sudo systemctl daemon-reload && systemctl enable nodedaemon-nc.service'
os.system(cmd_line)
##############################################################################


#######################################
# 13 configure  cc.conf
#######################################
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
# 14. configure sshfs
##############################################################################
cmd_line = 'sudo -u luhya ssh-keygen'
os.system(cmd_line)
cmd_line = "sudo -u luhya cat /home/luhya/.ssh/id_rsa.pub | ssh luhya@%s 'cat >> ~/.ssh/authorized_keys'" % ccip
os.system(cmd_line)
cmd_line = "sudo -u luhya ssh %s 'exit' " % ccip
os.system(cmd_line)

cmd_line = 'sudo chown -R luhya:luhya /storage/config'
commands.getoutput(cmd_line)

##############################################################################
# 14. clear download packages
##############################################################################
cmd_line = 'sudo chown -R luhya:luhya /storage && sudo chmod -R 777 /storage'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /usr/local/nodedaemon && sudo chmod -R 777 /usr/local/wnodedaemonww'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /var/log/educloud'
commands.getoutput(cmd_line)


print '----------------------------------------------------------'
print  'Now system will reboot to enable node daemon ... ... ...'
time.sleep(1)
print '... ... ... ... ...'
cmd_line = 'sudo reboot'
commands.getoutput(cmd_line)
