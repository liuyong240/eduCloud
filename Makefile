# Makefile
#
#

.PHONY: build clean

CLIENT_DEST		=debian/luhya-client
SERVER_DEST		=debian/luhya-server
SERVER_DEST_CN  =debian/luhya-server-cn

WEB_CLOUD       =debian/educloud-luhyacloud
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
	#     WEB_CLOUD    #
	####################
	install -d $(WEB_CLOUD)/usr/local/www/luhyacloud/
	install -d $(WEB_CLOUD)/var/log/educloud
	install -d $(WEB_CLOUD)/etc/educloud/modules

	cp $(CURDIR)/luhyacloud/*.py                        $(WEB_CLOUD)/usr/local/www/
	cp $(CURDIR)/luhyacloud/luhyacloud/*.py             $(WEB_CLOUD)/usr/local/www/luhyacloud/

	#####################
	#     WEB_PORTAL    #
	#####################
	install -d $(WEB_PORTAL)/usr/local/www/portal
	cp $(CURDIR)/luhyacloud/portal/*.py                 $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/conf              $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/static            $(WEB_PORTAL)/usr/local/www/portal/
	cp -r $(CURDIR)/luhyacloud/portal/templates         $(WEB_PORTAL)/usr/local/www/portal/

	##################
	#     WEB_CLC    #
	##################
	install -d $(WEB_CLC)/usr/local/www/clc
	cp $(CURDIR)/luhyacloud/clc/*.py                    $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/conf                 $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/static               $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/templates            $(WEB_CLC)/usr/local/www/clc/
	cp -r $(CURDIR)/luhyacloud/clc/sql                  $(WEB_CLC)/usr/local/www/clc/

	#####################
	#     WEB_WALRUS    #
	#####################
	install -d $(WEB_WALRUS)/usr/local/www/walrus
	cp $(CURDIR)/luhyacloud/walrus/*.py                 $(WEB_WALRUS)/usr/local/www/walrus/

	#################
	#     WEB_CC    #
	#################
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
	install -d $(DAEMON_NC)/usr/local/nodedaemon/nc
