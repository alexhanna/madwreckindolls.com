from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from django_localflavor_us.models import USStateField, USPostalCodeField, PhoneNumberField

# Requires django 1.5 for one-to-one User Profile extensions
# https://docs.djangoproject.com/en/1.5/topics/auth/#storing-additional-information-about-users
#
# Email address should be equal to the username
# Email is set in the User model
#
class Skater(models.Model):
    user = models.OneToOneField(User)
    phone = PhoneNumberField()
    derby_name = models.CharField("Derby Name", max_length=100)
    derby_number = models.CharField("Derby Number", max_length=50)

    address1 = models.CharField("Address 1", max_length=50)
    address2 = models.CharField("Address 2", max_length=50)
    city = models.CharField("City", max_length=50)
    state = USStateField()
    zip = USPostalCodeField()
    
    emergency_contact = models.CharField("Contact Name", max_length=100)
    emergency_phone = PhoneNumberField()
    emergency_relationship = models.CharField("Contact Relationship", max_length=50)

    insurance_provider = models.CharField("Insurance Provider", max_length=50)
    hospital = models.CharField("Preferred Hospital", max_length=50)
    medical_details = models.TextField("Medical Allergies and Other Info")




def create_skater_profile(sender, instance, created, **kwargs):
    if created:
        Skater.objects.create(user=instance)

post_save.connect(create_skater_profile, sender=User)



