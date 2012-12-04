from django_localflavor_us.forms import USPhoneNumberField, USZipCodeField
from django_localflavor_us.us_states import STATE_CHOICES
from legal_headache.models import LegalDocumentBinder, LegalDocument

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button

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
        label = "Emergency Phone",
        required = True,
    )
    
    emergency_relationship = forms.CharField(
        label = "Emergency Contact Relationship",
        max_length = 100,
        required = True,
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

    code_of_conduct = forms.CharField(
        widget = forms.Textarea(),
        required = False,
        label = "",
        #initial = LegalDocumentBinder.get_active_version_text('codeofconduct'),
    )
    code_of_conduct_agree = forms.BooleanField(
        label = "I agree to the Code of Conduct"
    )

    wftda = forms.CharField(
        widget = forms.Textarea(),
        required = False,
        label = "",
        #initial = LegalDocumentBinder.get_active_version_text('wftda'),
    )
    wftda_agree = forms.BooleanField(
        label = "I agree to the WFTDA Release"
    )

    mwd = forms.CharField(
        widget = forms.Textarea(),
        required = False,
        label = "",
        #initial = LegalDocumentBinder.get_active_version_text('mwd'),
    )
    mwd_agree = forms.BooleanField(
        label = "I agree to the MWD"
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
    payment_shit = forms.CharField(max_length=100)
