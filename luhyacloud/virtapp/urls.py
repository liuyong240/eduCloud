from django.conf.urls import patterns, url
from virtapp import views

urlpatterns = patterns('',
        url(r'^ldaps_setting$',     views.ldaps_setting,             name='ldaps_setting'),
        url(r'^vapp_mgr$',           views.vapp_mgr,                  name='vapp_mgr'),

        url(r'^vapp/add$',                              views.vapp_add,                   name='vapp_add'),
        url(r'^vapp/edit/(?P<appid>\w+)$',              views.vapp_edit,                  name='vapp_edit'),
        url(r'^vapp/permission/edit/(?P<appid>\w+)$',   views.vapp_perm_edit,             name='vapp_perm_edit'),


        url(r'^jt/vapps$',           views.jtable_vapps,              name='jtable_vapps'),

        ## API
        url(r'^api/1.0/set/ldaps/setting$',    views.set_ldaps_para,     name='set_ldaps_para'),
        url(r'^api/1.0/usercreate$',           views.usercreate,         name='usercreate'),
        url(r'^api/1.0/userdelete$',           views.userdelete,         name='userdelete'),
        url(r'^api/1.0/userupdate$',           views.userupdate,         name='userupdate'),
        url(r'^api/1.0/setpass$',              views.setpass,            name='setpass'),

        url(r'^api/1.0/vapp/list$',      views.list_vapp,               name='list_vapp'),
        url(r'^api/1.0/vapp/delete$',    views.delete_vapp,             name='delete_vapp'),
        url(r'^api/1.0/vapp/create$',    views.create_vapp,             name='create_vapp'),
        url(r'^api/1.0/vapp/edit$',      views.edit_vapp,               name='edit_vapp'),
        url(r'^api/1.0/perm/update$',    views.update_perm,             name='update_perm'),

    )