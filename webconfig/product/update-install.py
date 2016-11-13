import os, commands

cmd_line = 'sudo dpkg -i *.deb'
os.system(cmd_line)

cmd_line = 'tar vxf pip.tar -C /tmp/'
commands.getoutput(cmd_line)

cmd_line = 'rm /tmp/rsync_16.0.4.orig.tar.gz'
commands.getoutput(cmd_line)

cmd_line = 'export LC_ALL=C && sudo pip install /tmp/*.tar.gz'
os.system(cmd_line)

cmd_line = 'sudo chown -R luhya:luhya /storage && sudo chmod -R 777 /storage'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /usr/local/www && sudo chmod -R 777 /usr/local/www'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /usr/local/nodedaemon && sudo chmod -R 777 /usr/local/nodedaemon'
commands.getoutput(cmd_line)
cmd_line = 'sudo chown -R luhya:luhya /var/log/educloud'
commands.getoutput(cmd_line)