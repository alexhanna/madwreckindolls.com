from django.db import models
from django.contrib.auth.models import UserManager, BaseUserManager, AbstractBaseUser
from django_localflavor_us.models import USStateField, USPostalCodeField, PhoneNumberField
from datetime import datetime
from accounts.email import send_receipt_email
from mwd import settings

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
    """
    def create_stripe_customer(self, card_token):
        if not card_token:
            raise PaymentError("No credit card token sent with payment information. Our payment system can't charge a card if there is no card to charge...")
            return False

        customer_id = ""

        import stripe
        try:
            stripe.api_key = settings.STRIPE_SECRET
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
                    amount = self.balance * 100,
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
                    amount = charge.amount / 100,
                    method = "credit",
                    method_detail = str(charge.id) + " " + charge.card.type + " x" + str(charge.card.last4) + " " + str(charge.card.exp_month) + "/" + str(charge.card.exp_year),
                    description = description,
                    date = datetime.now(),
                )
            receipt.save()
            send_receipt_email(receipt, )

            self.balance = self.balance - (charge.amount / 100)
            self.save()







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

    account_create_date = models.DateTimeField(auto_now_add = True)
    account_modify_date = models.DateTimeField(auto_now = True)
    registration_completed = models.BooleanField("Registration Completed")




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

    paid_date = models.DateField(
        "Paid Date",
        blank = True,
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
def generate_scheduled_invoice(skater, schedule, description = False):

    """ Check to see if the invoice already exists for this skater """
    try:
        invoice = Invoice.objects.get(skater=skater, schedule=schedule)
        return invoice
    except Invoice.DoesNotExist:
        pass

    if not description:
        description = "Dues Payment - " + str(schedule)

    invoice = Invoice.objects.create(
                                skater = skater,
                                schedule = schedule,
                                invoice_date = datetime.now(),
                                due_date = schedule.due_date,
                                description = description,
                                amount = schedule.get_dues_amount(skater)
                            )
    
    b = skater.balance
    a = invoice.amount

    skater.balance = skater.balance + invoice.amount
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



