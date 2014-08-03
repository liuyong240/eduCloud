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
    url(r'^index$',         views.index_view,                         name='index_view'),


    )