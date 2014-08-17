from django.conf.urls import patterns, url
from cc import views

urlpatterns = patterns('',
    #url(r'^main/top/$',     views.admin_top_view,   name='main_top_view'),

    # API 1.0
    # this is a POST requtst, all data in POST section
    url(r'^api/1.0/imagebuild/(?P<srcid>\w+)/(?P<destid>\w+)/$', views.image_build,               name='images_build'),
    url(r'^api/1.0/register/host$',        views.register_host,               name='register_host'),
    url(r'^api/1.0/register/server$',      views.register_server,             name='register_server'),

    # Web Page

    )