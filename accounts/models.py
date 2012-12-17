from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser

from django_localflavor_us.models import USStateField, USPostalCodeField, PhoneNumberField
from mwd import settings


"""
# Requires django 1.5 for one-to-one User Profile extensions
# https://docs.djangoproject.com/en/1.5/topics/auth/#storing-additional-information-about-users
#
# Email address should be equal to the username
# Email is set in the User model
# 
# Useful: http://procrastinatingdev.com/django/using-configurable-user-models-in-django-1-5/
"""
class Skater(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    #objects = UserManager

    class Meta:
        verbose_name = "Skater"
        verbose_name_plural = "Skaters"
    
    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        if self.derby_name != '':
            return self.derby_name + ' (' + self.first_name + ' ' + self.last_name + ')'
        elif self.first_name != '' or self.last_name != '':
            return '(' + self.first_name + ' ' + self.last_name + ')'
        else:
            return 'Unnamed Skater (no name set)'

    def get_short_name(self):
        if self.derby_name != '':
            return self.derby_name
        elif self.first_name != '':
            return self.first_name
        else:
            return 'Unnamed Skater'

           
    derby_name = models.CharField(
        "Derby Name", 
        max_length = 100,
        blank = True,
    )

    derby_number = models.CharField(
        "Derby Number", 
        max_length=50,
        blank = True,
    )

    phone = PhoneNumberField(
        blank=True
    )

    address1 = models.CharField(
        "Address 1", 
        max_length = 50,
        blank = True,
    )

    address2 = models.CharField(
        "Address 2", 
        max_length=50,
        blank = True,
    )

    city = models.CharField(
        "City", 
        max_length = 50,
        blank = True,
    )

    state = USStateField(
        blank = True,
    )

    zip = USPostalCodeField(
        blank = True,
    )
    
    emergency_contact = models.CharField(
        "Emergency Contact Name", 
        max_length = 100,
        blank = True,
    )

    emergency_phone = PhoneNumberField(
        "Emergency Contact Phone",
        blank = True,
    )

    emergency_relationship = models.CharField(
        "Emergency Contact Relationship", 
        max_length=50,
        blank = True,
    )

    insurance_provider = models.CharField(
        "Insurance Provider", 
        max_length = 50,
        blank = True,
    )

    hospital = models.CharField(
        "Preferred Hospital", 
        max_length = 50,
        blank = True,
    )

    medical_details = models.TextField(
        "Medical Allergies and Other Info",
        blank = True,
    )

    balance = models.DecimalField(
        "Account Balance", 
        max_digits=10, 
        decimal_places=2,
        blank = True,
    )

    payment_preference = models.CharField(
        "Payment Preference",
        max_length = 15,
        choices = settings.PAYMENT_PREFERENCES,
        blank = True,
    )





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



class Invoice(models.Model):
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
    
    def __unicode__(self):
        return self.skater.derby_name + " - " + self.description + " - $" + str(self.amount)


    skater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    )

    invoice_date = models.DateField(
        "Invoice Date",
    )

    due_date = models.DateField(
        "Due Date",
    )
    
    description = models.TextField(
        "Invoice Description",
        blank = True,
    )
    
    INVOICE_STATUS_CHOICES = (
        ("paid", "Paid"),
        ("unpaid", "Unpaid"),
        ("cancelled", "Cancelled"),
    )

    status = models.CharField(
        "Invoice Status",
        max_length = "15",
        choices = INVOICE_STATUS_CHOICES,
        default = "unpaid",
    )

    amount = models.DecimalField(
        "Invoice Total", 
        max_digits=10, 
        decimal_places=2,
    )


class Receipt(models.Model):
    class Meta:
        verbose_name = "Payment Receipt"
        verbose_name_plural = "Payment Receipts"

    def __unicode__(self):
        return self.skater.derby_name + " - " + self.description + " - $" + str(self.amount)
    
    skater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    )

    amount = models.DecimalField(
        "Amount Paid", 
        max_digits=10, 
        decimal_places=2,
    )

    method = models.CharField(
        "Payment Method",
        max_length = 15,
        choices = settings.PAYMENT_METHODS,
    )

    method_detail = models.CharField(
        "Payment Details",
        max_length = 200,
        blank = True,
    )

    description = models.TextField(
        "Receipt Description"
    )
    
    date = models.DateField(
        "Payment Date",
    )



