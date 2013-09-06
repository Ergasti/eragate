from django.contrib import admin
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.core import urlresolvers

from vps.models import *
from openstack import is_nova_exception

admin.site.disable_action('delete_selected')

admin.site.register(Flavor)
admin.site.register(Plan)
admin.site.register(OSImage)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('placed_at', 'user', 'plan', 'fulfilled')
    actions = ['fulfill_orders']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.fulfilled: # obj is not None, so this is an edit
            return ['fulfillment_vps', 'user', 'plan', 'os_image']
        else:
            return []

    def fulfillment_vps(self, obj):
        change_url = urlresolvers.reverse('admin:vps_vps_change', args=(obj.vps.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.vps))
    fulfillment_vps.short_description = "VPS"

    def fulfill_orders(self, request, queryset):
        for order in queryset:
            try:
                order.fulfill()
                self.message_user(request, "Successfully fulfilled: %s" % order)
            except Exception as e:
                if is_nova_exception(e):
                    self.message_user(request, "Error fulfilling %s: %s" % (order, e),
                                      level=messages.ERROR)
                else:
                    raise
    fulfill_orders.short_description = "Launch instances to fulfill selected orders"
admin.site.register(Order, OrderAdmin)

class VPSAdmin(admin.ModelAdmin):
    list_display = ('ip', 'owner', 'plan')
    readonly_fields = ['instance_uuid', 'ip', 'order', 'vnc_link']

    def vnc_link(self, obj):
      try:
        url = obj.generate_vnc_console_link()
        return mark_safe('<a href="%s">Open VNC Console</a>' % (url))
      except:
        return "VNC Not Available"
    vnc_link.short_description = "VNC Console"

admin.site.register(VPS, VPSAdmin)
