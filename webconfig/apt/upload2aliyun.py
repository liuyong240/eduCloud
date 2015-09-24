import os, sys


DST_IP = '121.41.80.147'

cmd_line = 'scp -p /root/Downloads/*.deb root@%s:/root/Downloads/' % DST_IP
os.system(cmd_line)
cmd_line = 'scp -p /root/Downloads/depends/*.deb root@%s:/root/Downloads/depends/' % DST_IP
os.system(cmd_line)
cmd_line = 'scp -p /root/Downloads/client/*.deb root@%s:/root/Downloads/client/' % DST_IP
os.system(cmd_line)
cmd_line = 'scp -p /root/Downloads/client/depends/*.deb root@%s:/root/Downloads/client/depends/' % DST_IP
os.system(cmd_line)

cmd_line = 'scp -p /var/packages/scripts/*.py root@%s:/var/packages/scripts/' % DST_IP
os.system(cmd_line)
cmd_line = 'scp -p /var/packages/scripts/client/*.py root@%s:/var/packages/scripts/client/' % DST_IP
os.system(cmd_line)
#cmd_line = 'scp -p /var/packages/data* root@%s:/var/packages/' % DST_IP
#os.system(cmd_line)
cmd_line = 'scp -p /var/packages/pip.tar root@%s:/var/packages/' % DST_IP
os.system(cmd_line)

