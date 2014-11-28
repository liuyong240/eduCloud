from django.conf.urls import patterns, include, url
from django.contrib import admin
from luhyacloud import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'luhyacloud.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/',     include(admin.site.urls)),
    url(r'^clc/',       include('clc.urls')),
    url(r'^walrus/',    include('walrus.urls')),
    url(r'^cc/',        include('cc.urls')),
    url(r'^nc/',        include('nc.urls')),
    url(r'^sc/',        include('sc.urls')),

    url(r'^machine/cpu/util$',         views.machine_cpu_util,               name='machine_cpu_util'),
    url(r'^machine/net/util$',         views.machine_net_util,               name='machine_net_util'),
    url(r'^machine/mem/util$',         views.machine_mem_util,               name='machine_mem_util'),
    url(r'^machine/disk/util$',        views.machine_disk_util,               name='machine_disk_util'),
)
