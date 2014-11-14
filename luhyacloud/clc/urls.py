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
    url(r'^computers$',     views.computers_view,                     name='computers_view'),
    url(r'^hosts$',         views.hosts_view,                         name='hosts_view'),
    url(r'^settings$',      views.settings_view,                      name='settings_view'),
    url(r'^vss$',           views.vss_view,                           name='vss_view'),
    url(r'^rvds$',          views.rvds_view,                          name='rvds_view'),
    url(r'^lvds$',          views.lvds_view,                          name='lvds_view'),
    url(r'^tasks$',         views.tasks_view,                         name='tasks_view'),

    url(r'^adm_add_new_account',                    views.adm_add_new_account,              name='adm_add_new_account'),
    url(r'^admin_batch_add_new_accounts',           views.admin_batch_add_new_accounts,     name='admin_batch_add_new_accounts'),
    url(r'^request_new_account',                    views.request_new_account,              name='request_new_account'),
    url(r'^restore_password',                    views.restore_password,              name='restore_password'),
    url(r'^send_feedback',                    views.send_feedback,              name='send_feedback'),

    url(r'^user/edit_profile/(?P<uid>\w+)$',                    views.edit_profile,              name='edit_profile'),
    url(r'^user/edit_password/(?P<uid>\w+)$',                   views.edit_password,             name='edit_profile'),


    # image create and modify URL
    url(r'^image/create/task/begin/(?P<srcid>\w+)$',                                            views.start_image_create_task,            name='start_image_create_task'),

    url(r'^image/create/task/prepare/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',            views.prepare_image_create_task,          name='prepare_image_create_task'),
    url(r'^image/create/task/getprogress/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',        views.image_create_task_getprogress,      name='image_create_task_getprogress'),
    url(r'^image/create/task/prepare/success/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',    views.image_create_task_prepare_success,  name='image_create_task_prepare_success'),
    url(r'^image/create/task/prepare/failure/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',    views.image_create_task_prepare_failure,  name='image_create_task_prepare_failure'),

    url(r'^image/create/task/run/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',                views.run_image_create_task,              name='run_image_create_task'),
    url(r'^image/create/task/stop/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',               views.stop_image_create_task,             name='stop_image_create_task'),
    url(r'^image/create/task/getvmstatus/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',        views.image_create_task_getvmstatus,      name='image_create_task_getvmstatus'),
    url(r'^image/create/task/updatevmstatus/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)/(?P<vmstatus>\w+)$',        views.image_create_task_updatevmstatus,      name='image_create_task_updatevmstatus'),

    url(r'^image/create/task/submit/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',             views.submit_image_create_task,                 name='submit_image_create_task'),
    url(r'^image/create/task/getsubmitprogress/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',  views.image_create_task_getsubmitprogress,      name='image_create_task_getsubmitprogress'),
    url(r'^image/create/task/submit/failure/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',     views.image_create_task_submit_failure,         name='image_create_task_submit_failure'),
    url(r'^image/create/task/submit/success/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',     views.image_create_task_submit_success,         name='image_create_task_submit_success'),

    url(r'^image/create/task/view/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$',      views.image_create_task_view,      name='view_image_create_task'),

    url(r'^image/modify/task/begin/(?P<srcid>\w+)$',  views.start_image_modify_task,            name='start_image_modify_task'),

    # form URLs
    url(r'^cc/modify/resources/(?P<cc_name>\w+)$',      views.cc_modify_resources,                   name='cc_modify_resources'),

    # iframe page
    url(r'^jt/images$',             views.jtable_images,                 name='jtable_images_view'),
    url(r'^jt/tasks$',              views.jtable_tasks,                  name='jtable_tasks_view'),


    url(r'^jt/settings/authpath$',  views.jtable_settings_for_authapth,  name='jtable_settings_authpath_view'),
    url(r'^jt/settings/ostypes$',   views.jtable_settings_for_ostypes,   name='jtable_settings_ostypes_view'),
    url(r'^jt/settings/rbac$',      views.jtable_settings_for_rbac,      name='jtable_settings_rbac_view'),
    url(r'^jt/settings/vmusage$',   views.jtable_settings_for_vmusage,   name='jtable_settings_vmusage_view'),
    url(r'^jt/settings/serverrole', views.jtable_settings_for_serverrole,name='jtable_settings_serverrole_view'),
    url(r'^jt/settings/vmtypes',    views.jtable_settings_for_vmtypes,   name='jtable_settings_vmtypes_view'),

    url(r'^jt/servers/cc$',             views.jtable_servers_cc,                 name='jtable_servers_cc_view'),
    url(r'^jt/servers/nc$',             views.jtable_servers_nc,                 name='jtable_servers_nc_view'),
    url(r'^jt/servers/lnc$',            views.jtable_servers_lnc,                name='jtable_servers_lnc_view'),

    url(r'^jt/account/actived$',            views.jtable_active_accounts,                name='jtable_active_accounts'),
    url(r'^jt/account/inactive$',           views.jtable_inactive_accounts,              name='jtable_inactive_accounts'),

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

    url(r'^api/1.0/tasks/list$',          views.list_tasks,                 name='list_tasks_view'),
    url(r'^api/1.0/tasks/delete$',        views.delete_tasks,               name='delete_tasks_view'),

    # url(r'^api/1.0/hosts/list$',          views.list_hosts,                 name='list_hosts_view'),
    # url(r'^api/1.0/hosts/delete$',        views.delete_hosts,               name='delete_hosts_view'),
    # url(r'^api/1.0/hosts/update$',        views.update_hosts,               name='update_hosts_view'),
    # url(r'^api/1.0/hosts/create$',        views.create_hosts,               name='create_hosts_view'),
    #
    url(r'^api/1.0/servers/list$',                      views.list_servers,             name='list_servers_view'),
    url(r'^api/1.0/servers/list/(?P<roletype>\w+)$',    views.list_servers_by_role,     name='list_servers_by_role'),
    url(r'^api/1.0/servers/delete$',        views.delete_servers,               name='delete_servers_view'),
    url(r'^api/1.0/servers/update$',        views.update_servers,               name='update_servers_view'),
    url(r'^api/1.0/servers/create$',        views.create_servers,               name='create_servers_view'),

    url(r'^api/1.0/ccresource/list$',                   views.list_cc_resource,                 name='list_cc_resource_view'),
    url(r'^api/1.0/ccresource/list/(?P<recid>\w+)$',    views.list_cc_resource_by_id,           name='list_cc_resource_by_id_view'),
    url(r'^api/1.0/ccresource/delete$',        views.delete_cc_resource,               name='delete_cc_resource_view'),
    url(r'^api/1.0/ccresource/update$',        views.update_cc_resource,               name='update_cc_resource_view'),
    url(r'^api/1.0/ccresource/create$',        views.create_cc_resource,               name='create_cc_resource_view'),

    url(r'^api/1.0/account/active/list$',          views.list_active_account,                 name='list_active_account_view'),
    url(r'^api/1.0/account/active/delete$',        views.delete_active_account,               name='delete_active_account_view'),
    url(r'^api/1.0/account/active/update$',        views.update_active_account,               name='update_active_account_view'),
    url(r'^api/1.0/account/inactive/list$',        views.list_inactive_account,                 name='list_active_account_view'),

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


    # this is a POST requtst, all data in POST section
    url(r'^api/1.0/register/host$',        views.register_host,               name='register_host'),
    url(r'^api/1.0/register/server$',      views.register_server,             name='register_server'),
    url(r'^api/1.0/list/ncs$',             views.list_ncs,                    name='list_ncs'),

    # common api interface
    url(r'^api/1.0/getwalrusinfo$',                     views.get_walrus_info,             name='get_walrus_info'),
    url(r'^api/1.0/getimageinfo/(?P<imgid>\w+)$',       views.get_image_info,              name='get_image_info'),

    url(r'^api/1.0/account/create$',             views.account_create,                      name='account_create'),
    url(r'^api/1.0/account/create/batch$',       views.account_create_batch,                name='account_create_batch'),
    url(r'^api/1.0/account/request$',            views.account_request,                     name='account_request'),
    url(r'^api/1.0/account/update_profile$',     views.account_update_profile,              name='account_update_profile'),



    )
