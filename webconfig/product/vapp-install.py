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

if checkPackage('nodedaemon-clc') == False:
   print "--------------------------------------------------"
   print "Need to install cloud controller first.           "
   print "--------------------------------------------------"
   exit(1)

##############################################################################
# 7. install educloud in one machine by apt-get
##############################################################################
cmd_line = 'sudo apt-get -y install educloud-virtapp'
os.system(cmd_line)

cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
os.system(cmd_line)

# verify deb package install status
if checkPackage('educloud-virtapp') == False:
   print "--------------------------------------------------"
   print "Install educloud-virtapp Failed, please try again."
   print "--------------------------------------------------"
   exit(1)

##############################################################################
# 10. config django
##############################################################################
cmd_line= 'cd /usr/local/www/ && python manage.py syncdb'
os.system(cmd_line)

##############################################################################
# 14. clear download packages
##############################################################################
cmd_line = 'sudo rm /var/cache/apt/archives/*.deb'
commands.getoutput(cmd_line)
cmd_line = 'sudo rm /var/cache/apt/archives/partial/*.deb'
commands.getoutput(cmd_line)

print '----------------------------------------------------------'
print  'Now system will reboot to enable all clc  ... ... ...'
time.sleep(1)
print '... ... ... ... ...'
cmd_line = 'sudo reboot'
commands.getoutput(cmd_line)

