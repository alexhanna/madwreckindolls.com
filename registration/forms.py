from django_localflavor_us.forms import USPhoneNumberField, USZipCodeField
from django_localflavor_us.us_states import STATE_CHOICES
from legal_headache.models import LegalDocumentBinder, LegalDocument

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button
from mwd import settings


class PersonalForm(forms.Form):

    derby_name = forms.CharField(
        label = "Derby Name",
        help_text = "Optional. Here's some information about choosing a name.",
        max_length = 100,
        required = False,
    )
    
    derby_number = forms.CharField(
        label = "Derby Number",
        help_text = "Optional. Here's information about how to pick a valid derby number.",
        max_length = 50,
        required = False,
    )

    email = forms.EmailField(
        label = "Email Address",
        required = True,
    )

    phone = USPhoneNumberField(
        label = "Phone",
        required = True,
    )
    
    first_name = forms.CharField(
        label = "First Name",
        max_length = 50,
        required = True,
    )
    
    last_name = forms.CharField(
        label = "Last Name",
        max_length = 50,
        required = True,
    )

    address1 = forms.CharField(
        label = "Address",
        max_length = 100,
        required = True,
    )

    address2 = forms.CharField(
        label = "Address 2",
        max_length = 100,
        required = False,
    )

    city = forms.CharField(
        label = "City",
        max_length = 100,
        required = True,
    )

    state = forms.ChoiceField(
        widget = forms.Select(),
        choices = STATE_CHOICES,
        initial = "WI",
        required = True,
    )

    zip = USZipCodeField(
        label = "Zip Code",
        required = True,
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.add_input(Submit('submit', 'Next Step - Emergency Info'))
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '?'
        super(PersonalForm, self).__init__(*args, **kwargs)


class EmergencyForm(forms.Form):
    
    emergency_contact = forms.CharField(
        label = "Emergency Contact Name",
        max_length = 100,
        required = True,
    )
    
    emergency_phone = USPhoneNumberField(
        label = "Emergency Contact Phone Number",
        required = True,
    )
    
    emergency_relationship = forms.CharField(
        label = "Emergency Contact Relationship",
        max_length = 100,
        required = True,
    )

    wftda_confirm = forms.ChoiceField(
        label = "Do you have a WFTDA insurance number?",
        choices = (
            ('yes', "Yes"), 
            ('no', "No")
        ),
        widget = forms.RadioSelect,
    )

    wftda_number = forms.CharField(
        label = "WFTDA Number",
        max_length = 50,
        required = False,
        help_text = "If you know your WFTDA number, enter it here. If you don't, no big deal.",
    )

    insurance_company = forms.CharField(
        label = "Insurance Provider",
        help_text = "Do you have health insurance? Who is your insurance provider?",
        max_length = 100,
        required = False,
    )
    
    hospital_preference = forms.CharField(
        label = "Hospital Preference",
        help_text = "Do you have a preferred Madison area hospital?",
        max_length = 100,
        required = False,
    )

    allergies = forms.CharField(
        widget = forms.Textarea(),
        label = "Allergies and Medical Information",
        required = True,
        help_text = "Will latex kill you? If so, we should know.",
    )
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.add_input(Button('button', 'Back'))
        self.helper.add_input(Submit('submit', 'Next Step - Legal'))
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '?'
        super(EmergencyForm, self).__init__(*args, **kwargs)


class LegalForm(forms.Form):

    mwd = forms.CharField(
            widget = forms.Textarea(),
            required = False,
            label = "",
    )

    code_of_conduct_agree = forms.BooleanField(
        label = "I have read and agree to the Code of Conduct"
    )

    def __init__(self, *args, **kwargs):
        
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.add_input(Button('button', 'Back'))
        self.helper.add_input(Submit('submit', 'Next Step - Dues'))
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '?'
       
        super(LegalForm, self).__init__(*args, **kwargs)

class PaymentForm(forms.Form):
    
    payment_method = forms.ChoiceField(
        choices = settings.PAYMENT_PREFERENCES
    )
    
    stripe_token = forms.CharField(
        max_length = 64,
        required = False,
    )

    autobill = forms.BooleanField(
        required = False,
    )

    def clean(self):
        cleaned_data = super(PaymentForm, self).clean()

        ## Stripe token in blank and we're expecting to process a credit card
        if cleaned_data.get("payment_method") == "cc" and cleaned_data.get("stripe_token") == "":
            raise forms.ValidationError("Credit card payment type selected but we did not receive a valid credit card token from Stripe.")

        return cleaned_data

