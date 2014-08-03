from django.conf.urls import patterns, url
from clc import views

urlpatterns = patterns('',
    #url(r'^main/top/$',     views.admin_top_view,   name='main_top_view'),

    # API 1.0


    # Web Page
    url(r'^login$',                          views.logon_view,               name='logon_view'),
    )