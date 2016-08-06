import os, sys

if len(sys.argv) > 1:
    DST_IP = sys.argv[1]
else:
    DST_IP = '121.41.80.147'

cmd_line = 'scp -p /mnt/src/*.deb root@%s:/root/Downloads/' % DST_IP
os.system(cmd_line)

cmd_line = 'scp -p /mnt/src/eduCloud/webconfig/product/*.py root@%s:/var/packages/scripts/' % DST_IP
os.system(cmd_line)

cmd_line = 'scp -p /mnt/src/pip.tar root@%s:/var/packages/' % DST_IP
os.system(cmd_line)

cmd_line = 'scp -p /mnt/src/eduCloud/webconfig/apt/* root@%s:/root/apt/' % DST_IP
os.system(cmd_line)



