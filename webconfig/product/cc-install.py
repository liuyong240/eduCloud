import os, commands, sys, getopt
import time

def checkPackage( pname ):
    cmd_line = 'dpkg -l | grep %s' % pname
    output = commands.getoutput(cmd_line)
    if len(output) > 0 and output.split()[0] == 'ii':
       return True
    else:
       return False

def usage():
    print "Usage : cc-install [-h hostip ]"

def main(argv):
    DST_IP = '121.41.80.147'
    MODE = "w"

    try:
      opts, args = getopt.getopt(argv,"h:m:",["host=","mode="])
      for opt, arg in opts:
          if opt in ( "-h", "--host"):
             DST_IP =  arg
          if opt in ("-m", "--mode"):
             MODE = arg
    except getopt.GetoptError:
      pass

    ##############################################################################
    # 1. update /etc/apt/sources.list
    ##############################################################################
    if not os.path.exists('/etc/apt/sources.list.luhya'):
        cmd_line = 'sudo cp /etc/apt/sources.list /etc/apt/sources.list.luhya'
        commands.getoutput(cmd_line)

        cmd_line = 'cp /etc/apt/sources.list /tmp/'
        commands.getoutput(cmd_line)

        with open('/tmp/sources.list', MODE) as myfile:
            myfile.write('deb http://%s/debian/ zhejiang non-free' % DST_IP)

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

        #cmd_line = 'sudo passwd luhya'
        #os.system(cmd_line)

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
    cmd_line = 'sudo apt-get -y install nodedaemon-cc'
    os.system(cmd_line)

    cmd_line = 'sudo chown -R luhya:luhya /storage && sudo chmod -R 777 /storage'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo chown -R luhya:luhya /usr/local/www && sudo chmod -R 777 /usr/local/www'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo chown -R luhya:luhya /usr/local/nodedaemon && sudo chmod -R 777 /usr/local/wnodedaemonww'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo chown -R luhya:luhya /var/log/educloud'
    commands.getoutput(cmd_line)

    cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
    os.system(cmd_line)

    if checkPackage('educloud-cc') == False:
        print "--------------------------------------------------"
        print "Install educloud-cc Failed, please try again."
        print "--------------------------------------------------"
        exit(1)
    if checkPackage('nodedaemon-cc') == False:
       print "--------------------------------------------------"
       print "Install nodedaemon-cc Failed, please try again."
       print "--------------------------------------------------"
       exit(1)

    ##############################################################################
    # 8. install 3rd python and rsync lib
    ##############################################################################
    cmd_line = 'wget http://%s/pip.tar' % DST_IP
    os.system(cmd_line)

    cmd_line = 'tar vxf pip.tar -C /tmp/'
    commands.getoutput(cmd_line)

    cmd_line = 'rm /tmp/rsync_16.0.4.orig.tar.gz'
    commands.getoutput(cmd_line)

    cmd_line = 'rm /tmp/MySQL*.tar.gz'
    os.system(cmd_line)

    cmd_line = 'export LC_ALL=C && sudo pip install /tmp/*.tar.gz'
    os.system(cmd_line)

    cmd_line = 'sudo dpkg -i /tmp/*.deb'
    os.system(cmd_line)

    #cmd_line = 'sudo systemctl enable rsync && sudo systemctl start rsync'
    #os.system(cmd_line)

    cmd_line = 'rm pip.tar'
    commands.getoutput(cmd_line)

    ##############################################################################
    # 9. configure rabbitmq service
    ##############################################################################
    cmd_line = "sudo rabbitmqctl list_users | grep luhya | awk '{ print $1 }'"
    ret = commands.getoutput(cmd_line)
    if ret == '':
        cmd_line = 'sudo rabbitmqctl add_user luhya luhya'
        commands.getoutput(cmd_line)
        cmd_line = 'sudo rabbitmqctl set_permissions luhya  ".*" ".*" ".*" '
        commands.getoutput(cmd_line)
        cmd_line = 'sudo service rabbitmq-server restart'
        os.system(cmd_line)

    #######################################
    # 11&12 configure , clc.conf and cc.conf
    #######################################
    if checkPackage('nodedaemon-clc') == False:
        clcip  = raw_input("Enter Cloud IP    : ")
    else:
        clcip = "127.0.0.1"

    clcipstr = "IP=%s\n" % clcip
    with open('/storage/config/clc.conf', 'w') as myfile:
        myfile.write('[server]\n')
        myfile.write(clcipstr)

    ccname = raw_input("Enter Cluster Name: ")
    ccnamestr = "ccname=%s" % ccname
    with open('/storage/config/cc.conf', 'w') as myfile:
        myfile.write('[server]\n')
        myfile.write("IP=127.0.0.1\n")
        myfile.write(ccnamestr)

    ##############################################################################
    # 13. configure sshfs
    ##############################################################################
    if clcip == "127.0.0.1":
        pass
    else:
        cmd_line = 'sudo -u luhya ssh-keygen'
        os.system(cmd_line)
        cmd_line = "sudo -u luhya cat /home/luhya/.ssh/id_rsa.pub | ssh luhya@%s 'cat >> ~/.ssh/authorized_keys'" % clcip
        os.system(cmd_line)
        cmd_line = "sudo -u luhya ssh %s 'exit' " % clcip
        os.system(cmd_line)

    ##############################################################################
    # 14. clear download packages
    ##############################################################################
    cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo rm /var/cache/apt/archives/partial/*.deb'
    commands.getoutput(cmd_line)

    cmd_line = 'sudo chown -R luhya:luhya /storage && sudo chmod -R 777 /storage'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo chown -R luhya:luhya /usr/local/www && sudo chmod -R 777 /usr/local/www'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo chown -R luhya:luhya /usr/local/nodedaemon && sudo chmod -R 777 /usr/local/wnodedaemonww'
    commands.getoutput(cmd_line)
    cmd_line = 'sudo chown -R luhya:luhya /var/log/educloud'
    commands.getoutput(cmd_line)

    print '----------------------------------------------------------'
    print  'Now system will reboot to enable all services ... ... ...'
    time.sleep(1)
    print '... ... ... ... ...'
    cmd_line = 'sudo reboot'
    commands.getoutput(cmd_line)


if __name__ == "__main__":
   main(sys.argv[1:])

