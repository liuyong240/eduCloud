from django.conf.urls import patterns, url
from portal import views

urlpatterns = patterns('',

    # Web Page
    url(r'^$',                      views.portal_home,               name='portal_home'),
    url(r'^vdlogin$',               views.portal_login,              name='portal_login'),
    url(r'^admlogin$',              views.portal_adm_login,          name='portal_adm_login'),
    url(r'^cloud-desktops$',        views.portal_vds,                name='portal_vds'),
    url(r'^cloud-applications$',    views.portal_vapp,               name='portal_vapp'),

    )