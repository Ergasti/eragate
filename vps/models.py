import datetime, time, os

from django.conf import settings
from django.utils.timezone import utc
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField
from django.db.models import signals

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

    def getinfo(self):
       return "%s , %s months" % (self.flavor.name_en , self.months)


class OSImage(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s, %s" % (self.name, self.created_at)

subdomain_validator = RegexValidator(
                        regex='^[a-z0-9][-a-z0-9]*[a-z0-9]$',
                        message=_('Subdomain should consist of only a-z 0-9 and -'))
def subdomain_restriction(subdomain):
    if subdomain in settings.RESTRICTED_SUBDOMAINS:
        raise ValidationError(u'%s is not allowed' % subdomain)

class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)
    fulfilled_at = models.DateTimeField(editable=False, default=None, null=True)
    fulfilled = models.BooleanField(editable=False, default=False)
    subdomain = models.CharField(max_length=20, unique=True, validators=[subdomain_validator, subdomain_restriction])
    user = models.ForeignKey(User)
    plan = models.ForeignKey(Plan)
    os_image = models.ForeignKey(OSImage, null=True, blank=True)
    confirmed = models.BooleanField(blank=True, default=False)

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
                name="%s_%s" % (self.user.username, int(time.mktime(self.placed_at.utctimetuple()))),
                image=self.os_image_id,
                flavor=self.plan.flavor.flavor_uuid,
                meta={'owner': self.user.username, 'plan': str(self.plan_id), 'order': str(self.id)},
                key_name=params['key_name'],
                availability_zone=params['availability_zone'],
                nics=params['nics'],
                security_groups=params['security_groups'])
            vps.instance_uuid = server.id
            vps.subdomain = self.subdomain
            vps.save()

        if not vps.ip:
            floating_ip = nova_api().floating_ips.findall(instance_id=None)
            if floating_ip:
                floating_ip = floating_ip[0]
            else:
                floating_ip = nova_api().floating_ips.create(params['floating_ip_pool'])
            nova_api().servers.add_floating_ip(vps.instance_uuid, floating_ip)
            vps.ip = floating_ip.ip
            vps.register_subdomain()
            vps.save()

        self.fulfilled = True
        self.fulfilled_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()

class VPS(models.Model):
    owner = models.ForeignKey(User)
    plan = models.ForeignKey(Plan)
    instance_uuid = models.CharField(max_length=36)
    ip = models.CharField(max_length=15, null=True, blank=True)
    subdomain = models.CharField(max_length=20, unique=True, null=True, blank=True, validators=[subdomain_validator, subdomain_restriction])
    order = models.OneToOneField(Order, null=True, blank=True)

    def __unicode__(self):
        return "%s: %s, %s" % (self.owner, self.ip, self.instance_uuid)

    def get_instance_status(self):
        server = nova_api().servers.get(self.instance_uuid)
        return [server.__getattr__("OS-EXT-STS:vm_state"),
                server.__getattr__("OS-EXT-STS:task_state")]

    def generate_vnc_console_link(self):
        try: vnc_type = settings.OS_VNC_TYPE
        except: vnc_type = "novnc"
        return nova_api().servers.get_vnc_console(self.instance_uuid, vnc_type)['console']['url']

    def suspend_instance(self):
        return nova_api().servers.suspend(self.instance_uuid)

    def resume_instance(self):
        return nova_api().servers.resume(self.instance_uuid)

    def start_instance(self):
        return nova_api().servers.start(self.instance_uuid)

    def stop_instance(self):
        return nova_api().servers.stop(self.instance_uuid)

    def reboot_instance(self):
        return nova_api().servers.reboot(self.instance_uuid, 'SOFT')

    def force_reboot_instance(self):
        return nova_api().servers.reboot(self.instance_uuid, 'HARD')

    ZONE_FILE_MARKER = "VPS#"
    def __save_zone_data(self, zone_data):
        with open(settings.ZONE_FILE, "w") as zone_file:
            zone_file.writelines(zone_data)
        os.system(settings.ZONE_FILE_RELOAD_CMD)

    def register_subdomain(self):
        if not self.ip or not self.subdomain or not self.id:
            return
        zone_data = self.unregister_subdomain(False)
        zone_data.append("%s%s\tIN\tA\t%s ; %s%s\n" % (self.subdomain, settings.SUBDOMAIN_SUFFIX, self.ip, self.ZONE_FILE_MARKER, self.id))
        self.__save_zone_data(zone_data)

    def unregister_subdomain(self, save_and_reload=True):
        zone_data = open(settings.ZONE_FILE, "r").readlines()
        zone_data = [zone for zone in zone_data if zone.find("%s%s" % (self.ZONE_FILE_MARKER, self.id)) < 0]
        if save_and_reload:
            self.__save_zone_data(zone_data)
        else:
            return zone_data

def vps_save_callback(sender, instance, created, **kwargs):
    instance.register_subdomain()
def vps_delete_callback(sender, instance, using, **kwargs):
    instance.unregister_subdomain()
signals.post_save.connect(vps_save_callback, sender=VPS)
signals.pre_delete.connect(vps_delete_callback, sender=VPS)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True,related_name='profile')
    date_Of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20 , null=True)
    is_verfied = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=40 , null=True)
    sms_code = models.CharField(max_length=5 , null=True)
    status = models.CharField(max_length=400 , null=True)
    rating = models.FloatField(default=0.0)
    phone_is_verified=models.BooleanField(default=False)
    gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
     )
    gender = models.CharField(max_length=1, choices=gender_choices , null=True)
    USERNAME_FIELD = 'user.email'
    is_active = models.BooleanField('active', default=True,    # returns true if the user is still active
        help_text='Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    def __str__(self):
          return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserProfile.objects.get_or_create(user=instance)

signals.post_save.connect(create_user_profile, sender=User)
