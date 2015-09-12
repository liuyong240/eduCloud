import os, commands, sys
import time

def checkPackage( pname ):
    cmd_line = 'dpkg -l | grep %s' % pname
    output = commands.getoutput(cmd_line)
    if len(output) > 0 and output.split()[0] == 'ii':
       return True
    else:
       return False

##############################################################################
# 0. get the repository server IP
##############################################################################
if len(sys.argv) > 1:
    DST_IP = sys.argv[1]
else:
    DST_IP = '121.41.80.147'

##############################################################################
# 1. update /etc/apt/sources.list
##############################################################################
if not os.path.exists('/etc/apt/sources.list.luhya'):
    cmd_line = 'sudo cp /etc/apt/sources.list /etc/apt/sources.list.luhya'
    commands.getoutput(cmd_line)

    cmd_line = 'cp /etc/apt/sources.list /tmp/'
    commands.getoutput(cmd_line)

    with open('/tmp/sources.list', 'w') as myfile:
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

cmd_line = 'cd /tmp && wget http://%s/data' % DST_IP
os.system(cmd_line)
cmd_line = 'sudo mv /tmp/data /storage/images/data'
os.system(cmd_line)

##############################################################################
# 7. install educloud in one machine by apt-get
##############################################################################
cmd_line = 'sudo apt-get -y install nodedaemon-nc-kvm'
os.system(cmd_line)

cmd_line = 'sudo chown -R luhya:luhya /storage && sudo chmod -R 777 /storage'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /usr/local/nodedaemon && sudo chmod -R 777 /usr/local/wnodedaemonww'
commands.getoutput(cmd_line)

cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
os.system(cmd_line)

if checkPackage('nodedaemon-nc-kvm') == False:
   print "--------------------------------------------------"
   print "Install nodedaemon-nc-kvm Failed, please try again."
   print "--------------------------------------------------"
   exit(1)


cmd_line = 'sudo chown -R luhya:luhya /storage && sudo chmod -R 777 /storage'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /usr/local/www && sudo chmod -R 777 /usr/local/www'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /var/log/educloud'
commands.getoutput(cmd_line)

##############################################################################
# 8. install 3rd python and rsync lib
##############################################################################
cmd_line = 'wget http://%s/pip.tar' % DST_IP
os.system(cmd_line)
cmd_line = 'tar vxf pip.tar -C /tmp/'
commands.getoutput(cmd_line)
cmd_line = 'sudo dpkg -i /tmp/*.deb'
os.system(cmd_line)
cmd_line = 'rm pip.tar'
commands.getoutput(cmd_line)

##############################################################################
# 9. set bridge interface
# example as below :

# auto eth0
# iface eth0 inet manual
#
# auto br0
# iface br0 inet static
#     address xxx.xxx.xxx.xxx
#     netmask xxx.xxx.xxx.xxx
#     gateway xxx.xxx.xxx.xxx
#     bridge_ports eth0
#     bridge_stp off
#     bridge_fd 0
#     bridge_maxwait 0

#  virsh iface-bridge eth0 br0
#  brctl show
#  virsh -c qemu+ssh://luhya@192.168.99.100/system  list

##############################################################################


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
    cmd_line = "sudo -u luhya cat /home/luhya/.ssh/id_rsa.pub | ssh luhya@%s 'cat >> ~/.ssh/authorized_keys'" % ccip
    os.system(cmd_line)
    cmd_line = "sudo -u luhya ssh %s 'exit' " % ccip
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
