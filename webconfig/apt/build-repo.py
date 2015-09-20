import os, commands

cmd_line = 'id -u'
out = commands.getoutput(cmd_line)
if  out != '0':
    print "--------------------------------------------------"
    print "Need to run in root priviledge."
    exit(1)

print "--------------------------------------------------"
print "Create root directory ... "
cmd_line = 'mkdir -p /root/Downloads/client/depends'
os.system(cmd_line)
cmd_line = ' mkdir -p /root/Downloads/depends'
os.system(cmd_line)

print "--------------------------------------------------"
print "Install gnupg ... "
cmd_line = 'apt-get -y install gnupg'
os.system(cmd_line)

print "--------------------------------------------------"
print "Gen key ..."
cmd_line = 'gpg --gen-key'
os.system(cmd_line)

print "--------------------------------------------------"
print "Install reprepro ..."
cmd_line = 'apt-get -y install reprepro'
os.system(cmd_line)

print "--------------------------------------------------"
print "Create directory for /var/packages ..."
cmd_line = 'mkdir -p /var/packages/debian/conf'
os.system(cmd_line)

cmd_line = 'mkdir -p /var/packages/scripts/client'
os.system(cmd_line)

cmd_line = 'mkdir -p /var/packages/kvm'
os.system(cmd_line)

cmd_line = 'mkdir -p /var/packages/fedora'
os.system(cmd_line)

cmd_line = 'cp distributions options /var/packages/debian/conf'
os.system(cmd_line)

cmd_line = 'touch /var/packages/debian/conf/override.zhejiang'
os.system(cmd_line)

cmd_line = 'touch /var/packages/debian/conf/override.client'
os.system(cmd_line)

print "--------------------------------------------------"
print "Install nginx ..."
cmd_line = 'apt-get -y install nginx'
os.system(cmd_line)

cmd_line = 'cp educloud.conf /etc/nginx/sites-available/'
os.system(cmd_line)

cmd_line = 'cp server_names_hash_bucket_size.conf /etc/nginx/conf.d/'
os.system(cmd_line)

cmd_line = 'cd /etc/nginx/sites-enabled &&  rm default &&  ln -s ../sites-available/educloud.conf . &&  service nginx start'
os.system(cmd_line)

print "--------------------------------------------------"
print "Out packages.educloud.key ..."
cmd_line = 'gpg --armor --output /var/packages/packages.educloud.key --export thomas.li@educloud.com'
os.system(cmd_line)

print "--------------------------------------------------"
print "Successfully Done."














