import datetime

from django.contrib import admin
from django.conf import settings
from django.utils.timezone import utc
from django.contrib import messages

from vps.models import *
from openstack import is_nova_exception

admin.site.register(Flavor)
admin.site.register(Plan)
admin.site.register(OSImage)
admin.site.register(VPS)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('placed_at', 'user', 'plan', 'fulfilled')
    actions = ['fulfill_orders']

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
