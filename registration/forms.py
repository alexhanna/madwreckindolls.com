from django_localflavor_us.forms import USPhoneNumberField, USZipCodeField
from django_localflavor_us.us_states import STATE_CHOICES
from accounts.models import Skater
from legal.models import LegalDocumentBinder, LegalDocument

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button
from mwd import settings


class PersonalForm(forms.Form):

    email = forms.EmailField(
        label = "Email Address",
        required = True,
    )

    phone = USPhoneNumberField(
        label = "Phone",
        required = True,
    )

    dob = forms.DateField(
        label = "Date of Birth",
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

    derby_name = forms.CharField(
        label = "Derby Name",
        help_text = "Optional. <a href='https://docs.google.com/document/d/1dItDzn0uwGj2r_NAwsXh8doEpRi4HRtdRzat-ATJs5c/edit?pli=1' target='_blank'>Here's some information for choosing a name and number.</a>",
        max_length = 100,
        required = False,
    )
    
    derby_number = forms.CharField(
        label = "Derby Number",
        max_length = 50,
        required = False,
    )

    previous_level = forms.ChoiceField(
      label = "Derby Experience",
      help_text = "What level of derby experience do you have?<br><a href='https://docs.google.com/document/d/1HfJuTUF4QYCnesFTuTYmw0-W0PvWpoD9rbhYJicIgRA/edit?usp=sharing' target='_blank'>Click to read level descriptions.</a>",
      choices = Skater.DERBY_LAST_LEVELS,
      required = True,
    )

    hope_level = forms.ChoiceField(
      label = "I would prefer...",
      help_text = "For " + settings.REGISTRATION_SESSION_NAME + ", which level do you hope to be in?<br><a href='https://docs.google.com/document/d/1HfJuTUF4QYCnesFTuTYmw0-W0PvWpoD9rbhYJicIgRA/edit?usp=sharing' target='_blank'>Click to read level descriptions.</a>",
      choices = Skater.DERBY_HOPE_LEVELS,
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
        help_text = "Any latex, drug allergies or medical conditions we should know about?<br>If not, just tell us 'none'.",
    )

    first_aid_certified = forms.ChoiceField(
        choices = settings.BOOL_CHOICES,
        widget = forms.RadioSelect,
        initial = False,
        required = False,
        label = "Are you first aid certified?",
    )

    first_aid_volunteer = forms.ChoiceField(
        choices = settings.BOOL_CHOICES,
        widget = forms.RadioSelect,
        initial = False,
        required = False,
        label = "Interested in being a first aid volunteer?",
        help_text = "Are you willing to be a helper for first aid during practice or events, if necessary?",
    )
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.add_input(Button('button', 'Back'))
        self.helper.add_input(Submit('submit', 'Next Step'))
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

    mrd = forms.CharField(
            widget = forms.Textarea(),
            required = False,
            label = "",
    )

    code_of_conduct_agree = forms.BooleanField(
        label = """<b>By checking this box I certify that I have read, understand, and agree to abide by the above terms.</b>""",
        required = True,
    )
    

    def __init__(self, *args, **kwargs):
        
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.add_input(Button('button', 'Back'))
        self.helper.add_input(Submit('submit', 'Next Step'))
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '?'
       
        super(LegalForm, self).__init__(*args, **kwargs)

class AnythingElseForm(forms.Form):
    anything_else_registration = forms.CharField(
        widget = forms.Textarea(),
        label = "Is there anything else we should know?",
        required = False,
        help_text = "Examples:<ul><li>What's something nobody else knows about you?</li><li>Bacon is quite enjoyable.</li><li>I'm so excited for derby!</li><li>I can't wait to hit bitches!</li></ul>",
    )
    
    def __init__(self, *args, **kwargs):
        
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.add_input(Button('button', 'Back'))
        self.helper.add_input(Submit('submit', 'Next Step - Legal'))
        #self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '?'
       
        super(AnythingElseForm, self).__init__(*args, **kwargs)




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

