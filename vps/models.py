from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField
from django.db.models import signals
from django.db.models.signals import post_save

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

class OSImage(models.Model):
    uuid = models.CharField(max_length=32, primary_key=True)
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

class VPS(models.Model):
    owner = models.ForeignKey(User)
    plan = models.ForeignKey(Plan)
    instance_uuid = models.CharField(max_length=32)
    ip = models.CharField(max_length=15, null=True, blank=True)
    order = models.ForeignKey(Order, null=True, blank=True)

    def __unicode__(self):
        return "%s: %s, %s" % (self.owner, self.ip, self.instance_uuid)

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
