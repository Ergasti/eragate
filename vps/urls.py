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

    url(r'^suspend_instance/*', suspend_instance),
    url(r'^resume_instance/*', resume_instance),
    url(r'^start_instance/*', start_instance),
    url(r'^reboot_instance/*', reboot_instance),
    url(r'^force_reboot_instance/*', force_reboot_instance),
)
