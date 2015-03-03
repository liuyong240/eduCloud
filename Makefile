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

build:
	echo "now is building educloud debian packages ... ... "
clean:
	echo "now is cleaning educloud debian packages ... ... "
install:
	####################
	#     LUHYA API    #
	####################
	cd $(CURDIR)/webconfig/piplib/sharelib/educloud-luhyaapi || python setup.py sdist
	cp $(CURDIR)/webconfig/piplib/sharelib/educloud-luhyaapi/dist/*.tar.gz  $(CURDIR)/webconfig/piplib/3rd/
	rm -fr $(CURDIR)/webconfig/piplib/sharelib/educloud-luhyaapi/dist

	####################
	#     WEB_CLOUD    #
	####################
	install -d $(WEB_CLOUD)/var/log/educloud
	install -d $(WEB_CLOUD)/usr/local/www/educloud/
	install -d $(WEB_CLOUD)/usr/local/webconfig/3rd

	cp $(CURDIR)/luhyacloud/*.py                        $(WEB_CLOUD)/usr/local/www/
	cp $(CURDIR)/luhyacloud/luhyacloud/*.py             $(WEB_CLOUD)/usr/local/www/educloud/

	cp $(CURDIR)/debian/sudoers                         $(WEB_CLOUD)/usr/local/webconfig/
	cp -r $(CURDIR)/webconfig/apache2                   $(WEB_CLOUD)/usr/local/webconfig/
	cp -r $(CURDIR)/webconfig/rsync                     $(WEB_CLOUD)/usr/local/webconfig/
	cp $(CURDIR)/webconfig/piplib/3rd/*.tar.gz          $(WEB_CLOUD)/usr/local/webconfig/3rd/
	cp $(CURDIR)/webconfig/piplib/3rd/*.zip             $(WEB_CLOUD)/usr/local/webconfig/3rd/

	#####################
	#     WEB_PORTAL    #
	#####################
	install -d $(WEB_PORTAL)/usr/local/webconfig/
	cp $(CURDIR)/debian/sudoers                         $(WEB_PORTAL)/usr/local/webconfig/

	install -d $(WEB_PORTAL)/usr/local/www/portal
	cp $(CURDIR)/luhyacloud/portal/*.py                 $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/conf              $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/static            $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/templates         $(WEB_PORTAL)/usr/local/www/portal/

	##################
	#     WEB_CLC    #
	##################
	install -d $(WEB_CLC)/usr/local/webconfig/
	cp $(CURDIR)/debian/sudoers                         $(WEB_CLC)/usr/local/webconfig/

	install -d $(WEB_CLC)/etc/educloud/modules
	touch $(WEB_CLC)/etc/educloud/modules/clc

	install -d $(WEB_CLC)/usr/local/www/clc
	cp $(CURDIR)/luhyacloud/clc/*.py                    $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/conf                 $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/static               $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/templates            $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/sql                  $(WEB_CLC)/usr/local/www/clc/

	#####################
	#     WEB_WALRUS    #
	#####################
	install -d $(WEB_WALRUS)/usr/local/webconfig/
	cp $(CURDIR)/debian/sudoers                         $(WEB_WALRUS)/usr/local/webconfig/

	install -d $(WEB_WALRUS)/etc/educloud/modules
	touch $(WEB_WALRUS)/etc/educloud/modules/walrus

	install -d $(WEB_WALRUS)/usr/local/www/walrus
	cp $(CURDIR)/luhyacloud/walrus/*.py                 $(WEB_WALRUS)/usr/local/www/walrus/

	#################
	#     WEB_CC    #
	#################
	install -d $(WEB_CC)/usr/local/webconfig/
	cp $(CURDIR)/debian/sudoers                         $(WEB_CC)/usr/local/webconfig/

	install -d $(WEB_CC)/etc/educloud/modules
	touch $(WEB_CC)/etc/educloud/modules/cc

	install -d $(WEB_CC)/usr/local/www/cc
	cp $(CURDIR)/luhyacloud/cc/*.py                     $(WEB_CC)/usr/local/www/cc/

	#####################
	#     DAEMON_CLC    #
	#####################
	install -d $(DAEMON_CLC)/usr/local/nodedaemon/clc



	########################
	#     DAEMON_WALRUS    #
	########################
	install -d $(DAEMON_WALRUS)/usr/local/nodedaemon/walrus


	####################
	#     DAEMON_CC    #
	####################
	install -d $(DAEMON_CC)/usr/local/nodedaemon/cc


	####################
	#     DAEMON_NC    #
	####################
	install -d $(DAEMON_NC)/var/log/educloud
	install -d $(DAEMON_NC)/usr/local/nodedaemon/nc
	install -d $(DAEMON_NC)/usr/local/webconfig/3rd

	cp $(CURDIR)/debian/sudoers                         $(DAEMON_NC)/usr/local/webconfig/
	cp -r $(CURDIR)/webconfig/rsync                     $(DAEMON_NC)/usr/local/webconfig/
	cp $(CURDIR)/webconfig/piplib/3rd/*.tar.gz          $(DAEMON_NC)/usr/local/webconfig/3rd/
	cp $(CURDIR)/webconfig/piplib/3rd/*.zip             $(DAEMON_NC)/usr/local/webconfig/3rd/
