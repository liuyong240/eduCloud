from django.conf.urls import patterns, url
from portal import views

urlpatterns = patterns('',

    # Web Page
    url(r'^$',         views.portal_home,               name='portal_home'),

    )