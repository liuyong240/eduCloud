from django.conf.urls import patterns, url
from clc import views

urlpatterns = patterns('',
    #url(r'^main/top/$',     views.admin_top_view,   name='main_top_view'),

    # API 1.0
    # 1. Creating users
    # 2. Changing passwords
    # 3.


    # Web Page
    url(r'^login$',         views.display_login_window,               name='logon_view'),
    url(r'^user_login$',    views.user_login,                         name='user_login'),
    url(r'^user_logout$',   views.user_logout,                        name='user_logout'),
    url(r'^index$',         views.index_view,                         name='index_view'),
    url(r'^accounts$',      views.accounts_view,                      name='accounts_view'),
    url(r'^images$',        views.images_view,                        name='images_view'),
    url(r'^hosts$',         views.hosts_view,                         name='images_view'),
    url(r'^settings$',      views.settings_view,                      name='settings_view'),
    url(r'^vss$',           views.vss_view,                           name='vss_view'),
    url(r'^rvds$',          views.rvds_view,                          name='rvds_view'),
    url(r'^lvds$',          views.lvds_view,                          name='lvds_view'),
    url(r'^tasks$',         views.tasks_view,                         name='tasks_view'),


    # iframe page
    url(r'^jt/images$',             views.jtable_images,                 name='jtable_images_view'),
    url(r'^jt/settings/authpath$',  views.jtable_settings_for_authapth,  name='jtable_settings_authpath_view'),
    url(r'^jt/settings/ostypes$',   views.jtable_settings_for_ostypes,   name='jtable_settings_ostypes_view'),
    url(r'^jt/settings/rbac$',      views.jtable_settings_for_rbac,      name='jtable_settings_rbac_view'),
    url(r'^jt/settings/vmusage$',   views.jtable_settings_for_vmusage,   name='jtable_settings_vmusage_view'),
    url(r'^jt/settings/serverrole', views.jtable_settings_for_serverrole,name='jtable_settings_serverrole_view'),
    url(r'^jt/settings/vmtypes',    views.jtable_settings_for_vmtypes,   name='jtable_settings_vmtypes_view'),

    # API v1.0
    # system setting table ops by POST
    url(r'^api/1.0/settings/listauthpath$',      views.list_authpath,               name='list_authpath_view'),
    url(r'^api/1.0/settings/deleteauthpath$',    views.delete_authpath,             name='delete_authpath_view'),
    url(r'^api/1.0/settings/updateauthpath$',    views.update_authpath,             name='update_authpath_view'),
    url(r'^api/1.0/settings/createauthpath$',    views.create_authpath,             name='create_authpath_view'),
    url(r'^api/1.0/settings/authpath/option/list$',     views.authpath_optionlist,  name='authpath_optionlist_view'),


    url(r'^api/1.0/settings/listostypes$',       views.list_ostypes,               name='list_ostypes_view'),
    url(r'^api/1.0/settings/deleteostypes$',     views.delete_ostypes,             name='delete_ostypes_view'),
    url(r'^api/1.0/settings/updateostypes$',     views.update_ostypes,             name='update_ostypes_view'),
    url(r'^api/1.0/settings/createostypes$',     views.create_ostypes,             name='create_ostypes_view'),
    url(r'^api/1.0/settings/ostype/option/list$',     views.ostype_optionlist,  name='ostype_optionlist_view'),

    url(r'^api/1.0/settings/listrbac$',       views.list_rbac,               name='list_rbac_view'),
    url(r'^api/1.0/settings/deleterbac$',     views.delete_rbac,             name='delete_rbac_view'),
    url(r'^api/1.0/settings/updaterbac$',     views.update_rbac,             name='update_rbac_view'),
    url(r'^api/1.0/settings/createrbac$',     views.create_rbac,             name='create_rbac_view'),

    url(r'^api/1.0/settings/listserverrole$',       views.list_serverrole,               name='list_serverrole_view'),
    url(r'^api/1.0/settings/deleteserverrole$',     views.delete_serverrole,             name='delete_serverrole_view'),
    url(r'^api/1.0/settings/updateserverrole$',     views.update_serverrole,             name='update_serverrole_view'),
    url(r'^api/1.0/settings/createserverrole$',     views.create_serverrole,             name='create_serverrole_view'),
    url(r'^api/1.0/settings/serverrole/option/list$',     views.serverrole_optionlist,  name='serverrole_optionlist_view'),

    url(r'^api/1.0/settings/listvmtypes$',       views.list_vmtypes,               name='list_vmtypes_view'),
    url(r'^api/1.0/settings/deletevmtypes$',     views.delete_vmtypes,             name='delete_vmtypes_view'),
    url(r'^api/1.0/settings/updatevmtypes$',     views.update_vmtypes,             name='update_vmtypes_view'),
    url(r'^api/1.0/settings/createvmtypes$',     views.create_vmtypes,             name='create_vmtypes_view'),
    url(r'^api/1.0/settings/vmtype/option/list$',     views.vmtpye_optionlist,     name='vmtype_optionlist_view'),

    url(r'^api/1.0/settings/listvmusage$',       views.list_vmusage,               name='list_vmusage_view'),
    url(r'^api/1.0/settings/deletevmusage$',     views.delete_vmusage,             name='delete_vmusage_view'),
    url(r'^api/1.0/settings/updatevmusage$',     views.update_vmusage,             name='update_vmusage_view'),
    url(r'^api/1.0/settings/createvmusage$',     views.create_vmusage,             name='create_vmusage_view'),
    url(r'^api/1.0/settings/vmusage/option/list$',     views.vmusage_optionlist,     name='vmusage_optionlist_view'),

    # system core table ops by POST
    url(r'^api/1.0/images/list$',          views.list_images,                 name='list_images_view'),
    url(r'^api/1.0/images/delete$',        views.delete_images,               name='delete_images_view'),
    url(r'^api/1.0/images/update$',        views.update_images,               name='update_images_view'),
    url(r'^api/1.0/images/create$',        views.create_images,               name='create_images_view'),

    # url(r'^api/1.0/hosts/list$',          views.list_hosts,                 name='list_hosts_view'),
    # url(r'^api/1.0/hosts/delete$',        views.delete_hosts,               name='delete_hosts_view'),
    # url(r'^api/1.0/hosts/update$',        views.update_hosts,               name='update_hosts_view'),
    # url(r'^api/1.0/hosts/create$',        views.create_hosts,               name='create_hosts_view'),
    #
    # url(r'^api/1.0/servers/list$',          views.list_servers,                 name='list_servers_view'),
    # url(r'^api/1.0/servers/delete$',        views.delete_servers,               name='delete_servers_view'),
    # url(r'^api/1.0/servers/update$',        views.update_servers,               name='update_servers_view'),
    # url(r'^api/1.0/servers/create$',        views.create_servers,               name='create_servers_view'),
    #
    # url(r'^api/1.0/vapp/list$',          views.list_vapp,                 name='list_vapp_view'),
    # url(r'^api/1.0/vapp/delete$',        views.delete_vapp,               name='delete_vapp_view'),
    # url(r'^api/1.0/vapp/update$',        views.update_vapp,               name='update_vapp_view'),
    # url(r'^api/1.0/vapp/create$',        views.create_vapp,               name='create_vapp_view'),
    #
    # url(r'^api/1.0/vds/list$',          views.list_vds,                 name='list_vds_view'),
    # url(r'^api/1.0/vds/delete$',        views.delete_vds,               name='delete_vds_view'),
    # url(r'^api/1.0/vds/update$',        views.update_vds,               name='update_vds_view'),
    # url(r'^api/1.0/vds/create$',        views.create_vds,               name='create_vds_view'),
    #
    # url(r'^api/1.0/vss/list$',          views.list_vss,                 name='list_vss_view'),
    # url(r'^api/1.0/vss/delete$',        views.delete_vss,               name='delete_vss_view'),
    # url(r'^api/1.0/vss/update$',        views.update_vss,               name='update_vss_view'),
    # url(r'^api/1.0/vss/create$',        views.create_vss,               name='create_vss_view'),



    )
