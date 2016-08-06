import os, sys

cmd_line = 'cd /var/packages/debian && reprepro includedeb client   /root/Downloads/client/*.deb '
os.system(cmd_line)

cmd_line = 'cd /var/packages/debian && reprepro includedeb client   /root/Downloads/client/depends/*.deb'
os.system(cmd_line)


