# Makefile
#
#

.PHONY: build clean

WEB_CLOUD       =debian/educloud-core
WEB_PORTAL      =debian/educloud-portal
WEB_CLC         =debian/educloud-clc
WEB_WALRUS      =debian/educloud-walrus
WEB_CC          =debian/educloud-cc
WEB_NC          =debian/educloud-nc

DAEMON_CLC      =debian/nodedaemon-clc
DAEMON_WALRUS   =debian/nodedaemon-walrus
DAEMON_CC       =debian/nodedaemon-cc
DAEMON_NC       =debian/nodedaemon-nc

ALL_IN_ONE      =debian/all-in-one

build:
	echo "now is building educloud debian packages ... ... "
clean:
	echo "now is cleaning educloud debian packages ... ... "
install:
	####################
	#     LUHYA API    #
	####################
	cd $(CURDIR)/webconfig/piplib/sharelib/educloud-luhyaapi && python setup.py sdist
	cp $(CURDIR)/webconfig/piplib/sharelib/educloud-luhyaapi/dist/*.tar.gz  $(CURDIR)/webconfig/piplib/3rd/
	rm -fr $(CURDIR)/webconfig/piplib/sharelib/educloud-luhyaapi/dist
	cd $(CURDIR)/webconfig/piplib/3rd/ && tar cvf $(CURDIR)/../pip.tar *.gz *.deb

	####################
	#     WEB_CLOUD    #
	####################
	install -d $(WEB_CLOUD)/etc/educloud/modules
	touch $(WEB_CLOUD)/etc/educloud/modules/core

	install -d $(WEB_CLOUD)/usr/local/www/luhyacloud/
	install -d $(WEB_CLOUD)/usr/local/webconfig/3rd/web

	cp $(CURDIR)/luhyacloud/*.py                        $(WEB_CLOUD)/usr/local/www/
	python -m compileall $(CURDIR)/luhyacloud/luhyacloud/
	mv $(CURDIR)/luhyacloud/luhyacloud/*.pyc             $(WEB_CLOUD)/usr/local/www/luhyacloud/
	#cp $(CURDIR)/luhyacloud/luhyacloud/*.py              $(WEB_CLOUD)/usr/local/www/luhyacloud/
	cp $(CURDIR)/luhyacloud/luhyacloud/wsgi.py           $(WEB_CLOUD)/usr/local/www/luhyacloud/
	rm $(WEB_CLOUD)/usr/local/www/luhyacloud/wsgi.pyc

	cp $(CURDIR)/debian/sudoers                         $(WEB_CLOUD)/usr/local/webconfig/
	cp -r $(CURDIR)/webconfig/apache2                   $(WEB_CLOUD)/usr/local/webconfig/
	cp -r $(CURDIR)/webconfig/rsync                     $(WEB_CLOUD)/usr/local/webconfig/

	#####################
	#     WEB_PORTAL    #
	#####################
	install -d $(WEB_PORTAL)/etc/educloud/modules
	touch $(WEB_PORTAL)/etc/educloud/modules/portal

	install -d $(WEB_PORTAL)/usr/local/www/portal
	python -m compileall $(CURDIR)/luhyacloud/portal/
	mv $(CURDIR)/luhyacloud/portal/*.pyc                $(WEB_PORTAL)/usr/local/www/portal/
	#cp $(CURDIR)/luhyacloud/portal/*.py		    $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/conf              $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/static            $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/templates         $(WEB_PORTAL)/usr/local/www/portal/

	##################
	#     WEB_CLC    #
	##################
	install -d $(WEB_CLC)/etc/educloud/modules
	touch $(WEB_CLC)/etc/educloud/modules/clc
	cp $(CURDIR)/debian/educloud.conf                   $(WEB_CLC)/etc/educloud/modules/

	install -d $(WEB_CLC)/usr/local/www/clc
	python -m compileall $(CURDIR)/luhyacloud/clc/
	mv $(CURDIR)/luhyacloud/clc/*.pyc                   $(WEB_CLC)/usr/local/www/clc/
	#cp $(CURDIR)/luhyacloud/clc/*.py		    $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/conf                 $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/static               $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/templates            $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/sql                  $(WEB_CLC)/usr/local/www/clc/

	#####################
	#     WEB_WALRUS    #
	#####################
	install -d $(WEB_WALRUS)/etc/educloud/modules
	touch $(WEB_WALRUS)/etc/educloud/modules/walrus

	install -d $(WEB_WALRUS)/usr/local/www/walrus
	python -m compileall $(CURDIR)/luhyacloud/walrus/
	mv $(CURDIR)/luhyacloud/walrus/*.pyc                $(WEB_WALRUS)/usr/local/www/walrus/
	#cp $(CURDIR)/luhyacloud/walrus/*.py		    $(WEB_WALRUS)/usr/local/www/walrus/

	#################
	#     WEB_CC    #
	#################
	install -d $(WEB_CC)/etc/educloud/modules
	touch $(WEB_CC)/etc/educloud/modules/cc

	install -d $(WEB_CC)/usr/local/www/cc
	python -m compileall $(CURDIR)/luhyacloud/cc/
	mv $(CURDIR)/luhyacloud/cc/*.pyc                    $(WEB_CC)/usr/local/www/cc/
	#cp $(CURDIR)/luhyacloud/cc/*.py                     $(WEB_CC)/usr/local/www/cc/

	install -d $(WEB_CC)/usr/local/webconfig
	cp $(CURDIR)/debian/fuse.conf                       $(WEB_CC)/usr/local/webconfig/

	#####################
	#     DAEMON_CLC    #
	#####################
	install -d $(DAEMON_CLC)/usr/local/nodedaemon/clc

	cd $(CURDIR)/nodeDaemon/clc && su -c "pyinstaller clc_daemon.py -F -s" luhya
	cp $(CURDIR)/nodeDaemon/clc/dist/clc_daemon            $(DAEMON_CLC)/usr/local/nodedaemon/clc

	install -d $(DAEMON_CLC)/usr/local/bin/
	cp $(CURDIR)/webconfig/scripts/nodedaemon-clc          $(DAEMON_CLC)/usr/local/bin


	########################
	#     DAEMON_WALRUS    #
	########################
	install -d $(DAEMON_WALRUS)/usr/local/nodedaemon/walrus

	cd $(CURDIR)/nodeDaemon/walrus && su -c "pyinstaller walrus_daemon.py -F -s" luhya
	cp $(CURDIR)/nodeDaemon/walrus/dist/walrus_daemon            $(DAEMON_WALRUS)/usr/local/nodedaemon/walrus

	install -d $(DAEMON_WALRUS)/usr/local/bin/
	cp $(CURDIR)/webconfig/scripts/nodedaemon-walrus          $(DAEMON_WALRUS)/usr/local/bin

	####################
	#     DAEMON_CC    #
	####################
	install -d $(DAEMON_CC)/usr/local/nodedaemon/cc

	cd $(CURDIR)/nodeDaemon/cc && su -c "pyinstaller cc_daemon.py -F -s" luhya
	cp $(CURDIR)/nodeDaemon/cc/dist/cc_daemon            $(DAEMON_CC)/usr/local/nodedaemon/cc

	install -d $(DAEMON_CC)/usr/local/bin/
	cp $(CURDIR)/webconfig/scripts/nodedaemon-cc          $(DAEMON_CC)/usr/local/bin

	####################
	#     DAEMON_NC    #
	####################
	install -d $(DAEMON_NC)/usr/local/nodedaemon/nc
	install -d $(DAEMON_NC)/usr/local/webconfig/node/3rd

	cp $(CURDIR)/debian/sudoers                         $(DAEMON_NC)/usr/local/webconfig/node
	cp -r $(CURDIR)/webconfig/rsync                     $(DAEMON_NC)/usr/local/webconfig/node/

	cd $(CURDIR)/nodeDaemon/nc && su -c "pyinstaller nc_daemon.py -F -s" luhya
	cp $(CURDIR)/nodeDaemon/nc/dist/nc_daemon            $(DAEMON_NC)/usr/local/nodedaemon/nc

	install -d $(DAEMON_NC)/etc/educloud/modules
	touch $(DAEMON_NC)/etc/educloud/modules/nc

	cp $(CURDIR)/debian/fuse.conf                       $(DAEMON_NC)/usr/local/webconfig/node

	install -d $(DAEMON_NC)/usr/local/bin/
	cp $(CURDIR)/webconfig/scripts/nodedaemon-nc          $(DAEMON_NC)/usr/local/bin

	#####################
	#     ALL_IN_ONE    #
	#####################

	install -d $(ALL_IN_ONE)/etc/educloud/modules
	touch $(ALL_IN_ONE)/etc/educloud/modules/core
	touch $(ALL_IN_ONE)/etc/educloud/modules/portal
	touch $(ALL_IN_ONE)/etc/educloud/modules/clc
	touch $(ALL_IN_ONE)/etc/educloud/modules/walrus
	touch $(ALL_IN_ONE)/etc/educloud/modules/cc
	touch $(ALL_IN_ONE)/etc/educloud/modules/nc

	install -d $(ALL_IN_ONE)/usr/local/bin/

	install -d $(ALL_IN_ONE)/usr/local/webconfig/3rd/web

	cp $(CURDIR)/debian/fuse.conf                       $(ALL_IN_ONE)/usr/local/webconfig/
	cp $(CURDIR)/debian/sudoers                         $(ALL_IN_ONE)/usr/local/webconfig/
	cp -r $(CURDIR)/webconfig/apache2                   $(ALL_IN_ONE)/usr/local/webconfig/
	cp -r $(CURDIR)/webconfig/rsync                     $(ALL_IN_ONE)/usr/local/webconfig/

	cp $(CURDIR)/webconfig/scripts/all-in-one           $(ALL_IN_ONE)/usr/local/bin/

	############### WEB_CLOUD
	install -d $(ALL_IN_ONE)/usr/local/www/luhyacloud/

	cp $(CURDIR)/luhyacloud/*.py                         $(ALL_IN_ONE)/usr/local/www/
	python -m compileall $(CURDIR)/luhyacloud/luhyacloud/
	mv $(CURDIR)/luhyacloud/luhyacloud/*.pyc             $(ALL_IN_ONE)/usr/local/www/luhyacloud/
	cp $(CURDIR)/luhyacloud/luhyacloud/wsgi.py           $(ALL_IN_ONE)/usr/local/www/luhyacloud/
	rm $(ALL_IN_ONE)/usr/local/www/luhyacloud/wsgi.pyc

	############### WEB_PORTAL
	install -d $(ALL_IN_ONE)/usr/local/www/portal
	python -m compileall $(CURDIR)/luhyacloud/portal/
	mv $(CURDIR)/luhyacloud/portal/*.pyc                $(ALL_IN_ONE)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/conf              $(ALL_IN_ONE)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/static            $(ALL_IN_ONE)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/templates         $(ALL_IN_ONE)/usr/local/www/portal/

	############### WEB_CLC
	cp $(CURDIR)/debian/educloud.conf                   $(ALL_IN_ONE)/etc/educloud/modules/

	install -d $(ALL_IN_ONE)/usr/local/www/clc
	python -m compileall $(CURDIR)/luhyacloud/clc/
	mv $(CURDIR)/luhyacloud/clc/*.pyc                   $(ALL_IN_ONE)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/conf                 $(ALL_IN_ONE)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/static               $(ALL_IN_ONE)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/templates            $(ALL_IN_ONE)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/sql                  $(ALL_IN_ONE)/usr/local/www/clc/

	############### WEB_WALRUS
	install -d $(ALL_IN_ONE)/usr/local/www/walrus
	python -m compileall $(CURDIR)/luhyacloud/walrus/
	mv $(CURDIR)/luhyacloud/walrus/*.pyc                $(ALL_IN_ONE)/usr/local/www/walrus/

	############### WEB_CC
	install -d $(ALL_IN_ONE)/usr/local/www/cc
	python -m compileall $(CURDIR)/luhyacloud/cc/
	mv $(CURDIR)/luhyacloud/cc/*.pyc                    $(ALL_IN_ONE)/usr/local/www/cc/

	############### DAEMON_CLC
	install -d $(ALL_IN_ONE)/usr/local/nodedaemon/clc

	cp $(CURDIR)/nodeDaemon/clc/dist/clc_daemon            $(ALL_IN_ONE)/usr/local/nodedaemon/clc
	rm -fr $(CURDIR)/nodeDaemon/clc/dist        $(CURDIR)/nodeDaemon/clc/build

	############### DAEMON_WALRUS
	install -d $(ALL_IN_ONE)/usr/local/nodedaemon/walrus

	cp $(CURDIR)/nodeDaemon/walrus/dist/walrus_daemon            $(ALL_IN_ONE)/usr/local/nodedaemon/walrus
	rm -fr $(CURDIR)/nodeDaemon/walrus/dist     $(CURDIR)/nodeDaemon/walrus/build

	############### DAEMON_CC
	install -d $(ALL_IN_ONE)/usr/local/nodedaemon/cc

	cp $(CURDIR)/nodeDaemon/cc/dist/cc_daemon            $(ALL_IN_ONE)/usr/local/nodedaemon/cc
	rm -fr $(CURDIR)/nodeDaemon/cc/dist        $(CURDIR)/nodeDaemon/cc/build

	############### DAEMON_NC
	install -d $(ALL_IN_ONE)/usr/local/nodedaemon/nc

	cp $(CURDIR)/nodeDaemon/nc/dist/nc_daemon            $(ALL_IN_ONE)/usr/local/nodedaemon/nc
	rm -fr $(CURDIR)/nodeDaemon/nc/dist        $(CURDIR)/nodeDaemon/nc/build

