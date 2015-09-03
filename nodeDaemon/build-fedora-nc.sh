#! /bin/bash

#1. build nc-daemon
cd nc
pyinstaller nc_daemon.py -F -s


#2. upload nc related files
scp dist/nc_daemon fedora/nodedaemon-nc.service fedora/sudoers ../../webconfig/piplib/3rd/fedora/rsync*.rpm ../../webconfig/product/nc-install-fedora.py root@121.41.80.147:/var/packages/fedora/

#3. clean
rm -fr build/ dist/
rm *.spec

