import os, commands

# 1. update /etc/apt/sources.list
if not os.path.exists('/etc/apt/sources.list.luhya'):
    cmd_line = 'sudo cp /etc/apt/sources.list /etc/apt/sources.list.luhya'
    print cmd_line
    commands.getoutput(cmd_line)

    cmd_line = 'cp /etc/apt/sources.list /tmp/'
    print cmd_line
    commands.getoutput(cmd_line)

    with open('/tmp/sources.list', 'a') as myfile:
        myfile.write('deb http://121.41.80.147/debian/ zhejiang non-free')

    cmd_line = 'sudo cp /tmp/sources.list /etc/apt/sources.list'
    print cmd_line
    commands.getoutput(cmd_line)

# 2. Import the repository's public key
cmd_line = 'curl http://121.41.80.147/packages.educloud.key > /tmp/packages.educloud.key'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'sudo apt-key add /tmp/packages.educloud.key'
print cmd_line
commands.getoutput(cmd_line)

# 3. Fetch the list of packages available at the new source
cmd_line = 'sudo apt-get update'
print cmd_line
os.system(cmd_line)

# 3.1 install mysql-server without password prompt
with open('/tmp/mysql-server.list', 'w') as myfile:
    myfile.write('mysql-server mysql-server/root_password password root\n')
    myfile.write('mysql-server mysql-server/root_password_again password root\n')

cmd_line = 'sudo debconf-set-selections /tmp/mysql-server.list'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'sudo apt-get -y install mysql-server'
print cmd_line
commands.getoutput(cmd_line)

# 4. install educloud in one machine by apt-get
cmd_line = 'sudo apt-get -y install educloud-portal nodedaemon-clc nodedaemon-walrus nodedaemon-cc nodedaemon-nc'
print cmd_line
os.system(cmd_line)

# 5.1 configure /etc/clc.conf
cmd_line = 'echo "[server]"    > /tmp/clc.conf'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'echo "IP=127.0.0.1"  >> /tmp/clc.conf'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'sudo cp /tmp/clc.conf  /storage/config/clc.conf'
print cmd_line
commands.getoutput(cmd_line)

# 5.2 configure , cc.conf
cmd_line = 'echo "[server]"    > /tmp/cc.conf'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'echo "IP=127.0.0.1"  >> /tmp/cc.conf'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'echo "ccname=allinone"  >> /tmp/cc.conf'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'sudo cp /tmp/cc.conf  /storage/config/cc.conf'
print cmd_line
commands.getoutput(cmd_line)

cmd_line = 'sudo chown -R luhya:luhya /storage/config'
print cmd_line
commands.getoutput(cmd_line)

# 6. configure rabbitmq service
# ignored

# 7. configure sshfs
# ignored


# 8. clear download packages
cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
commands.getoutput(cmd_line)
cmd_line = 'sudo rm /var/cache/apt/archives/partial/*.deb'
commands.getoutput(cmd_line)
