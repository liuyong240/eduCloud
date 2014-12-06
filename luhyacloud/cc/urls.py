from django.conf.urls import patterns, url
from cc import views

urlpatterns = patterns('',
    #url(r'^main/top/$',     views.admin_top_view,   name='main_top_view'),

    # API 1.0
    # this is a POST requtst, all data in POST section
    url(r'^api/1.0/image/create/task/prepare$',     views.prepare_image_create_task,       name='prepare_image_create_task'),
    url(r'^api/1.0/image/create/task/run$',         views.run_image_create_task,           name='run_image_create_task'),
    url(r'^api/1.0/image/create/task/stop$',        views.stop_image_create_task,          name='stop_image_create_task'),
    url(r'^api/1.0/image/create/task/submit$',      views.submit_image_create_task,        name='submit_image_create_task'),
    url(r'^api/1.0/image/create/task/removeIPtables$',      views.removeIPtables_image_create_task,        name='removeIPtables_image_create_task'),

    url(r'^api/1.0/register/host$',        views.register_host,               name='register_host'),
    url(r'^api/1.0/register/server$',      views.register_server,             name='register_server'),

    url(r'^api/1.0/getimageversion/(?P<imgid>\w+)$',      views.get_images_version,          name='get_images_version'),

    )