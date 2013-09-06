from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gbvp.views.home', name='home'),
    # url(r'^gbvp/', include('gbvp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'vps.views.index'),
    url(r'^register/*', 'vps.views.UserRegistration'),
    url(r'^login/*', 'vps.views.login'),
    url(r'^order/*', 'vps.views.order'),
    url(r'^plan_order/(?P<plan>\w+)', 'vps.views.order_withplan'),
    url(r'^dashboard/*', 'vps.views.dashboard'),

    url(r'^suspend_instance/*', 'vps.views.suspend_instance'),
    url(r'^resume_instance/*', 'vps.views.resume_instance'),
    url(r'^start_instance/*', 'vps.views.start_instance'),
    url(r'^reboot_instance/*', 'vps.views.reboot_instance'),
    url(r'^force_reboot_instance/*', 'vps.views.force_reboot_instance'),
    



)
