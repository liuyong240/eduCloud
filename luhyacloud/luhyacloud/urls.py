from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'luhyacloud.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^clc/', include('clc.urls')),
    url(r'^walrus/', include('walrus.urls')),
    url(r'^cc/', include('cc.urls')),
    url(r'^nc/', include('nc.urls')),
    url(r'^sc/', include('sc.urls')),
)
