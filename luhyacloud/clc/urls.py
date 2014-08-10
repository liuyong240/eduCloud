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
    url(r'^jt/images$',         views.jtable_images,               name='jtable_images_view'),



    # API v1.0
    url(r'^api/1.0/images/listimages$',         views.list_images,                 name='list_images_view'),
    url(r'^api/1.0/images/deleteimages',        views.delete_images,               name='delete_images_view'),
    url(r'^api/1.0/images/updateimages',        views.update_images,               name='update_images_view'),
    url(r'^api/1.0/images/createimages',        views.create_images,               name='create_images_view'),

    )
