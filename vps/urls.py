from django.conf.urls import patterns, url

from vps.views import *

urlpatterns = patterns('',
    url(r'^$', index),
    url(r'^register/*', UserRegistration),
    url(r'^login/*', login),
    url(r'^order/*', order),
    url(r'^plan_order/(?P<plan>\w+)', order_withplan),
    url(r'^confirm_order/*', confirm_order),
    url(r'^dashboard/*', dashboard),
    url(r'^vps_action/(?P<action>\w{0,50})/(?P<vps>\w{0,50})/$', vps_action),
    url(r'^logout/*', logout_view),
)
