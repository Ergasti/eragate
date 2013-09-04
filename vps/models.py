from django.db import models
from django.contrib.auth.models import User

from djmoney.models.fields import MoneyField

class Flavor(models.Model):
    name_en = models.CharField(max_length=100, null=True)
    name_ar = models.CharField(max_length=100, null=True, blank=True)
    ram_mb = models.IntegerField()
    disk_gb = models.IntegerField()
    flavor_uuid = models.CharField(max_length=32, null=True, blank=True)

    def __unicode__(self):
        return "%s: %s MB, %s GB" % (self.name_en or self.name_ar, self.ram_mb, self.disk_gb)

class Plan(models.Model):
    months = models.IntegerField()
    flavor = models.ForeignKey(Flavor)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='EGP')

    def __unicode__(self):
        return "%s months, %s" % (self.months, self.flavor)

class VPS(models.Model):
    owner = models.ForeignKey(User)
    plan = models.ForeignKey(Plan)
    instance_uuid = models.CharField(max_length=32)
    ip = models.CharField(max_length=15, null=True, blank=True)

    def __unicode__(self):
        return "%s: %s, %s" % (self.owner, self.ip, self.instance_uuid)
