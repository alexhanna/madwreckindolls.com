from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from django_localflavor_us.models import USStateField, USPostalCodeField, PhoneNumberField


"""
# Requires django 1.5 for one-to-one User Profile extensions
# https://docs.djangoproject.com/en/1.5/topics/auth/#storing-additional-information-about-users
#
# Email address should be equal to the username
# Email is set in the User model
#
"""
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

"""
" Skater Status model
"   Provides default values for billing and describing the status of that Skater.
"   Helps provide us with an idea if the skater is active.
"""
class SkaterStatus(models.Model):
    class Meta:
        verbose_name = "Skater Status"
        verbose_name_plural = "Skater Statuses"
    
    def __unicode__(self):
        return self.name


    name = models.CharField(
        "Status Name", 
        max_length=50, 
        help_text = "Example: 'injured', 'active', 'administion', 'social'",
    )

    dues_amount = models.DecimalField(
        "Dues Amount", 
        max_digits = 10,
        decimal_places = 2,
        default = 0.00,
        help_text = "Dollar amount that we should bill these users for each billing period.",
    )



"""
" Skating session model
"   Provides grouping for billing periods and statistics
"""
class SkateSession(models.Model):
    class Meta:
        verbose_name = "Skating Session"
        verbose_name_plural = "Skating Sessions"
    
    def __unicode__(self):
        return self.name

    name = models.CharField(
        "Session Name", 
        max_length = 50,
        help_text = "Name of the session. Keep it simple, examples: 'Fall 2012', 'Summer 2013'")

    start_date = models.DateField(
        "Start Date",
        help_text = "Start date for this session. Used for informational purposes only.",
    )

    end_date = models.DateField(
        "End Date",
        help_text = "End date for this session. Used for informational purposes only.",
    )


"""
" Skating Session payment schedule
"   Provies a model for structuring billing dates and dues amounts
"""
class SkateSessionPaymentSchedule(models.Model):
    class Meta:
        verbose_name = "Dues Billing Date"
        verbose_name_plural = "Dues Billing Dates"

    session = models.ForeignKey(
        SkateSession,
        help_text = "Select the Session that this billing period is associated with.",
    )
    
    bill_date = models.DateField(
        "Due Date",
        help_text = "The date that payments are due for this billing period. We will attempt to charge credit cards on this date.",
    )

    start_date = models.DateField(
        "Start Date",
        help_text = "Start date for this billing period. This date will show up on their receipt.",
    )

    end_date = models.DateField(
        "End Date",
        help_text = "End date for this billing period. This date will show up on their receipt.",
    )

    dues_amounts = models.ManyToManyField(
        SkaterStatus, 
        through='SkateSessionPaymentAmount',
    )


"""
" Skate session payment amount
"   Provides a way to handle custom payment amounts for billing peroids
"""
class SkateSessionPaymentAmount(models.Model):
    class Meta:
        verbose_name = "Custom Dues Billing Amount"
        verbose_name_plural = "Custom Dues Billing Amounts"

    status = models.ForeignKey(SkaterStatus)
    
    dues_amount = models.DecimalField(
        "Custom Dues Amount", 
        max_digits=10, 
        decimal_places=2,
        help_text = "The amount we should bill Skaters matching this status for the billing period specified above.",
    )

    schedule = models.ForeignKey(SkateSessionPaymentSchedule)


