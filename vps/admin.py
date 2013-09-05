from django.contrib import admin
from vps.models import *

admin.site.register(Flavor)
admin.site.register(Plan)
admin.site.register(VPS)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('placed_at', 'user', 'plan', 'fulfilled')

admin.site.register(Order, OrderAdmin)
