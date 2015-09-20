import os, sys

cmd_line = 'cd /var/packages/debian && rm -fr db dists pool'
os.system(cmd_line)

cmd_line = 'cd /var/packages/debian && reprepro includedeb zhejiang /root/Downloads/*.deb'
os.system(cmd_line)

cmd_line = 'cd /var/packages/debian && reprepro includedeb zhejiang /root/Downloads/depends/*.deb'
os.system(cmd_line)