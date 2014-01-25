from django.db import models
from django.contrib.auth.models import UserManager, BaseUserManager, AbstractBaseUser
from django_localflavor_us.models import USStateField, PhoneNumberField
from datetime import datetime
from accounts.email import send_receipt_email
from mwd import settings
from mwd.utilities import random_string
from django.db.models.signals import pre_save
from django.dispatch import receiver
from decimal import *

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^django_localflavor_us\.models\.USStateField"])
add_introspection_rules([], ["^django_localflavor_us\.models\.USPostalCodeField"])
add_introspection_rules([], ["^django_localflavor_us\.models\.PhoneNumberField"])


class PaymentError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


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
        return self.name.title()


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
" Requires django 1.5
"
" Email address should be equal to the username
" Email is set in the User model
" 
" Useful: http://procrastinatingdev.com/django/using-configurable-user-models-in-django-1-5/
"         https://docs.djangoproject.com/en/1.5/topics/auth/#auth-custom-user
"""

class SkaterUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email = SkaterUserManager.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class Skater(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = SkaterUserManager()

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

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    """
    Get the stripe customer object, create one for this user if it doesnt exist
    """
    def get_stripe_customer(self, card_token = False):
        customer = False
        if self.stripe_customer_id:
            import stripe
            try:
                stripe.api_key = settings.STRIPE_SECRET
                customer = stripe.Customer.retrieve(self.stripe_customer_id)
            except stripe.InvalidRequestError, e:
                customer = False
            except e:
                pass

        if customer:
            return customer
        else:
            return self.create_stripe_customer(card_token)

    """
    Create a new stripe customer and save the customer ID
    
    Legacy function - This was (and still sort of is) used for the registration scripts.
    Replaced by update_stripe_customer below.
    """
    def create_stripe_customer(self, card_token):
        return self.update_stripe_customer(card_token)


    """ Get the current active stripe card token associated with this customer id """
    def get_active_stripe_card_token(self):
        if self.stripe_customer_id == '':
            return False

        import stripe
        stripe.api_key = settings.STRIPE_SECRET
        try:
            cust = stripe.Customer.retrieve(self.stripe_customer_id)
        except:
            raise PaymentError("There was a problem with our payment provider. Contact finance@madwreckindolls.com for help. Sorry :(")

        return cust.active_card

        

    def update_stripe_card_description( self, card_token = False):
        if not card_token:
            card_token = self.get_active_stripe_card_token()

        if not card_token:
            return

        self.stripe_card_description = card_token.type + " x" + str(card_token.last4) + " " + str(card_token.exp_month) + "/" + str(card_token.exp_year)
        self.save()



    """
    Update a Stripe Customer's credit card token. If a customer does not exist for this skater, create it.
    """
    def update_stripe_customer(self, card_token):
        if not card_token:
            raise PaymentError("No credit card token sent with payment information. Our payment system can't charge a card if there is no card to charge...")
        
        import stripe
        stripe.api_key = settings.STRIPE_SECRET

        """ Customer exists... update the card info. """
        if self.stripe_customer_id != "":
            try:
                cust = stripe.Customer.retrieve(self.stripe_customer_id)
                cust.card = card_token
                cust.save()

                return cust

            except stripe.CardError, e:
                body = e.json_body
                err = body['error']
                raise PaymentError("An error occured with your card. " + str(err['message']) + ".")

            except stripe.InvalidRequestError:
                pass

        """ Customer doesn't exist. We need to create them. """
        try:
            customer = stripe.Customer.create(
                description = self.get_full_name(),
                card = card_token,
                email = self.email,
            )
            customer_id = customer.id
        except stripe.InvalidRequestError, e:
            raise PaymentError("An error occured with our payment provider. Please try again and contact us if you still have issues.")
        except:
            raise PaymentError("An error occured with our payment provider. Please try again and contact us if you still have issues.")
        
        self.stripe_customer_id = customer_id
        self.save()

        return customer



    def card_on_file(self):
        if self.stripe_customer_id != "":
            return True
        else:
            return False


    """
    Charge Stripe Customer
    """
    def charge_credit_card(self, description):

        if self.card_on_file() is False:
            raise PaymentError("No credit card on file.")

        if self.balance > 0:
            import stripe
            try:
                stripe.api_key = settings.STRIPE_SECRET
                charge = stripe.Charge.create(
                    amount = int(self.balance) * 100,
                    currency = "usd",
                    customer = self.stripe_customer_id,
                    description = description,
                )
            except stripe.StripeError, e:
                raise PaymentError("There was a problem charing your card. Try again and contact us if you continue to receive this message.")
            except e:
                raise PaymentError("There was a problem communicating with our payment provider. Try again and contact us if you continue to receive this message.")

            if charge.card.cvc_check == "fail":
                raise PaymentError("That CVC code does not appear to be correct. The CVC code is either the 3-digit (Visa, MC, Disc.) or 4-digit (AMEX) code on the front or back of your card.")

            "Payment succeeded."

            receipt = Receipt(
                    skater = self,
                    amount = float(charge.amount) / 100,
                    fee = float(charge.fee_details[0].amount) / 100.0,
                    method = "credit",
                    method_detail = str(charge.id) + " " + charge.card.type + " x" + str(charge.card.last4) + " " + str(charge.card.exp_month) + "/" + str(charge.card.exp_year),
                    description = description,
                    date = datetime.now(),
                )
            receipt.save()
            send_receipt_email(receipt, )

            self.balance = self.balance - (charge.amount / 100)
            self.save()
            
            self.set_unpaid_invoices_paid(charge.amount / 100.0)


    """ Get unpaid invoices for this user and return them as a friendly bundle """
    def get_unpaid_invoices(self):
        return Invoice.objects.filter(skater=self).filter(status="unpaid")

    
    """ Get unpaid invoices short name for billing / invoicing purposes """
    def get_unpaid_invoices_description(self):
        invoices = self.get_unpaid_invoices()
        
        """ No unpaid invoices """
        if len(invoices) == 0:
            return ""

        """ It's just a single invoice """
        if len(invoices) == 1:
            return str(invoices[0])

        """ Multiple unpaid invoices """
        """
        invoices_desc = []

        for inv in invoices:
            invoices_desc.append('#' + str(inv.id))

        return "Invoices " + ', '.join(invoices_desc)
        """
        return ""


    """ Mark invoices as paid
    Automatically detect the invoices that are open and mark them as paid
    """
    def set_unpaid_invoices_paid(self, amount_paid):
        invoice_total = 0

        """ Check that the amount_paid matches the total amount on the invoices """
        invoices = self.get_unpaid_invoices()
        for inv in invoices:
            invoice_total = invoice_total + inv.amount

        if invoice_total == amount_paid:
            for inv in invoices:
                inv.mark_paid()



    DERBY_LAST_LEVELS = (
        ('', '- - - - - - -'),
        ('New', 'I am new to Derby'),
        ('101', '101 - Skating Skills'),
        ('151', '151 - Derby Skills'),
        ('201', '201 - Derby Strategy'),
        ('251', '251 - Derby Strategy'),
    )

    DERBY_HOPE_LEVELS = (
        ('', '- - - - - - -'),
        ('Not sure', 'Not sure'),
        ('101', '101 - Skating Skills'),
        ('151', '151 - Derby Skills'),
        ('201', '201 - Derby Strategy'),
        ('251', '251 - Derby Strategy'),
    )


    email = models.EmailField(
        "Email Address",
        max_length = 254, 
        unique = True,
        db_index = True,
    )

    is_active = models.BooleanField(
        default = True
    )

    is_admin = models.BooleanField(
        default = False
    )

    first_name = models.CharField(
        "First Name",
        max_length = 100,
        blank = True,
    )

    last_name = models.CharField(
        "Last Name",
        max_length = 100,
        blank = True,
    )
           
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

    zip = models.CharField(
        max_length = 20,
        blank = True,
    )

    dob = models.DateField(
        "Date of Birth",
        blank = True,
        null = True,
    )

    last_level = models.CharField(
        max_length = 8,
        blank = True,
        choices = DERBY_LAST_LEVELS,
    )

    hope_level = models.CharField(
        max_length = 8,
        blank = True,
        choices = DERBY_HOPE_LEVELS,
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

    wftda_number = models.CharField(
        "WFTDA Number",
        max_length = 50,
        blank = True,
        help_text = "WFTDA Insurance Number",
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

    first_aid_certified = models.BooleanField(
        "First Aid Certified",
        choices = settings.BOOL_CHOICES,
        blank = True,
    )

    first_aid_volunteer = models.BooleanField(
        "First Aid Volunteer",
        choices = settings.BOOL_CHOICES,
        blank = True,
    )

    anything_else_registration = models.TextField(
        "Anything else we should know?",
        blank = True,
    )

    balance = models.DecimalField(
        "Account Balance", 
        max_digits=10, 
        decimal_places=2,
        blank = True,
        default = 0,
    )

    payment_preference = models.CharField(
        "Payment Preference",
        max_length = 15,
        choices = settings.PAYMENT_PREFERENCES,
        blank = True,
    )

    status = models.ForeignKey(
        SkaterStatus,
        default = None,
        blank = True,
        null = True,
    )

    automatic_billing = models.BooleanField(
        "Automatic Billing",
        default = False,
    )
    
    stripe_customer_id = models.CharField(
        "Stripe Customer ID",
        max_length = 32,
        blank = True,
    )

    stripe_card_description = models.CharField(
        "Stripe Credit Card Description",
        max_length = 32,
        blank = True,
    )

    def set_user_hash(self, force = False):
        if force or self.user_hash == '':
            self.user_hash = random_string(32)

    user_hash = models.CharField(max_length=50, unique = True)
    account_create_date = models.DateTimeField(auto_now_add = True)
    account_modify_date = models.DateTimeField(auto_now = True)
    registration_completed = models.DateTimeField(auto_now = False, blank = True)

@receiver(pre_save, sender=Skater)
def skater_save_handler(sender, instance, **kwargs):
    instance.set_user_hash()





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
        ordering = ["start_date"]

    def __unicode__(self):
        return self.session.name + ' - ' + str(self.start_date) + ' to ' + str(self.end_date)

    session = models.ForeignKey(
        SkateSession,
        help_text = "Select the Session that this billing period is associated with.",
    )
    
    due_date = models.DateField(
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
    " Get the dues amount for this billing period by skater OR status
    " If a custom amount is set for their status this billing period, use that.
    " Otherwise default to the value set for the SkaterStatus value
    """
    def get_dues_amount(self, skater=False, status=False):
        if skater:
            status = skater.status

        try:
            return SkateSessionPaymentAmount.objects.get(schedule=self, status=status).dues_amount
        except SkateSessionPaymentAmount.DoesNotExist:
            return status.dues_amount


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



"""
" Invoice for dues
"""

class Invoice(models.Model):
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = [ "-invoice_date" ]
    
    def __unicode__(self):
        return self.skater.derby_name + " - " + self.description + " - $" + str(self.amount)

    def mark_paid(self):
        if self.status != "paid":
            self.status = "paid"
            self.paid_date = datetime.now()
            self.save()


    skater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    )

    schedule = models.ForeignKey(
        SkateSessionPaymentSchedule,
    )

    invoice_date = models.DateField(
        "Invoice Date",
        blank = True,
        null = True,
    )

    due_date = models.DateField(
        "Due Date",
        blank = True,
        null = True,
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

    paid_date = models.DateField(
        "Paid Date",
        blank = True,
        null = True,
    )

    amount = models.DecimalField(
        "Invoice Total", 
        max_digits=10, 
        decimal_places=2,
    )


"""
" Generate an invoice
" If that invoice already exists
" Create an invoice for a skater during a specified scheduling period.
" schedule.get_dues_amount will automatically determine the amount that should be billed.
"""
def generate_scheduled_invoice(skater, schedule, description = False, amount = -1):

    """ Check to see if the invoice already exists for this skater """
    try:
        invoice = Invoice.objects.get(skater=skater, schedule=schedule)
        return invoice
    except Invoice.DoesNotExist:
        pass

    """ Custom Description """
    if not description:
        description = "Dues - " + str(schedule)

    """ Custom Dues Amount """
    if amount == -1:
        amount = schedule.get_dues_amount(skater)
    else:
        amount = Decimal(amount)

    invoice = Invoice.objects.create(
                                skater = skater,
                                schedule = schedule,
                                invoice_date = datetime.now(),
                                due_date = schedule.due_date,
                                description = description,
                                amount = amount
                            )
    
    skater.balance = skater.balance + amount
    skater.save()

    return invoice


"""
" Receipts for Skaters
" Keep a record of transactions for users
" If a Skater pays by credit card, we should email them a receipt
"""

class Receipt(models.Model):
    class Meta:
        verbose_name = "Payment Receipt"
        verbose_name_plural = "Payment Receipts"
        ordering = [ "-date" ]

    def __unicode__(self):
        return self.skater.derby_name + " - " + self.description + " - $" + str(self.amount)

    skater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    )

    amount = models.DecimalField(
        "Amount Paid", 
        max_digits = 10, 
        decimal_places = 2,
    )
    
    fee = models.DecimalField(
        "Fee", 
        max_digits = 10, 
        decimal_places = 2,
        default = 0,
        help_text = "Payment provider fees for this transaction.",
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



