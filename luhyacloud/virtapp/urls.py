from django.conf.urls import patterns, url
from virtapp import views

urlpatterns = patterns('',
        url(r'^ldaps_setting$',     views.ldaps_setting,             name='ldaps_setting'),
        url(r'^vapp_mgr',           views.vapp_mgr,                  name='vapp_mgr'),

        ## API
        url(r'^api/1.0/set/ldaps/setting',    views.set_ldaps_para,     name='set_ldaps_para'),
        url(r'^api/1.0/usercreate',           views.usercreate,         name='usercreate'),
        url(r'^api/1.0/userdelete',           views.userdelete,         name='userdelete'),
        url(r'^api/1.0/userupdate',           views.userupdate,         name='userupdate'),
        url(r'^api/1.0/setpass',              views.setpass,            name='setpass'),
    )