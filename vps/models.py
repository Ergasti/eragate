import datetime

from django.conf import settings
from django.utils.timezone import utc

from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField

from openstack import nova_api, OS_VM_CREATION_SETTINGS_DEFAULTS

class Flavor(models.Model):
    name_en = models.CharField(max_length=100, null=True)
    name_ar = models.CharField(max_length=100, null=True, blank=True)
    ram_mb = models.IntegerField()
    disk_gb = models.IntegerField()
    flavor_uuid = models.CharField(max_length=36, null=True, blank=True)

    def __unicode__(self):
        return "%s: %s MB, %s GB" % (self.name_en or self.name_ar, self.ram_mb, self.disk_gb)

class Plan(models.Model):
    months = models.IntegerField()
    flavor = models.ForeignKey(Flavor)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='EGP')

    def __unicode__(self):
        return "%s months, %s" % (self.months, self.flavor)

class OSImage(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)
    fulfilled_at = models.DateTimeField(editable=False, default=None, null=True)
    fulfilled = models.BooleanField(editable=False, default=False)

    user = models.ForeignKey(User)
    plan = models.ForeignKey(Plan)
    os_image = models.ForeignKey(OSImage)

    def __unicode__(self):
        return "Order: %s ordering %s" % (self.user, self.plan)

    def fulfill(self):
        global OS_VM_CREATION_SETTINGS_DEFAULTS
        params = OS_VM_CREATION_SETTINGS_DEFAULTS.copy()
        params.update(settings.OS_VM_CREATION_SETTINGS)

        vps = VPS.objects.get_or_create(owner=self.user, plan=self.plan,
                                        order=self)[0]
        if not vps.instance_uuid:
            server = nova_api().servers.create(
                name="%s_%s" % (self.user.username, self.placed_at),
                image=self.os_image_id,
                flavor=self.plan.flavor.flavor_uuid,
                meta={'owner': self.user.username, 'plan': self.plan_id, 'order': self.id},
                key_name=params['key_name'],
                availability_zone=params['availability_zone'],
                nics=params['nics'],
                security_groups=params['security_groups'])
            vps.instance_uuid = server.id
            vps.save()

        if not vps.ip:
            floating_ip = nova_api().floating_ips.findall(instance_id=None)
            if floating_ip:
                floating_ip = floating_ip[0]
            else:
                floating_ip = nova_api().floating_ips.create(params['floating_ip_pool'])
            nova_api().add_floating_ip(vps.instance_uuid, floating_ip)
            vps.ip = floating_ip.ip
            vps.save()

        self.fulfilled = True
        self.fulfilled_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()

class VPS(models.Model):
    owner = models.ForeignKey(User)
    plan = models.ForeignKey(Plan)
    instance_uuid = models.CharField(max_length=36)
    ip = models.CharField(max_length=15, null=True, blank=True)
    order = models.ForeignKey(Order, null=True, blank=True)

    def __unicode__(self):
        return "%s: %s, %s" % (self.owner, self.ip, self.instance_uuid)
