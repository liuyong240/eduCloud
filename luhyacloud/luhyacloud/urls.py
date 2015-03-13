from django.conf.urls import patterns, include, url
from django.contrib import admin
from luhyacloud import views
import os
from settings import DEBUG

admin.autodiscover()

urlpatterns = patterns('',
        url(r'^admin/',     include(admin.site.urls)),
        url(r'^machine/cpu/util$',         views.machine_cpu_util,               name='machine_cpu_util'),
        url(r'^machine/net/util$',         views.machine_net_util,               name='machine_net_util'),
        url(r'^machine/mem/util$',         views.machine_mem_util,               name='machine_mem_util'),
        url(r'^machine/disk/util$',        views.machine_disk_util,               name='machine_disk_util'),

        url(r'^machine/get_service_status',        views.get_service_status,               name='get_service_status'),
        url(r'^machine/get_hardware_status$',      views.get_hardware_status,              name='get_hardware_status'),
    )

if DEBUG == True:
    urlpatterns += patterns('',
        url(r'^$',              include('portal.urls')),
        url(r'^portal/',        include('portal.urls')),
        url(r'^clc/',           include('clc.urls')),
        url(r'^walrus/',        include('walrus.urls')),
        url(r'^cc/',            include('cc.urls')),
    )
else:
    if os.path.exists("/etc/educloud/modules/portal") == True:
        urlpatterns += patterns('',
            url(r'^$',              include('portal.urls')),
            url(r'^portal/',        include('portal.urls')),
        )

    if os.path.exists("/etc/educloud/modules/clc") == True:
        urlpatterns += patterns('',
            url(r'^clc/',       include('clc.urls')),
        )

    if os.path.exists("/etc/educloud/modules/walrus") == True:
        urlpatterns += patterns('',
            url(r'^walrus/',    include('walrus.urls')),
        )

    if os.path.exists("/etc/educloud/modules/cc") == True:
        urlpatterns += patterns('',
            url(r'^cc/',    include('cc.urls')),
        )
