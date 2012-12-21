from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from accounts.models import Skater, SkateSession, SkateSessionPaymentSchedule, Invoice, Receipt
from registration.forms import PersonalForm, EmergencyForm, LegalForm, PaymentForm
from registration.email import send_registration_email
from legal_headache.models import LegalDocumentBinder, LegalDocument, LegalDocumentSignature
from mwd import settings
from mwd.utilities import get_client_ip


# If pre-registration is going on, only allow existing accounts to access the page for pre-registration
# Returns False if the user is ineligible for pre-reg
# Returns True if they are eligible for pre-reg
def can_pre_reg(request):
    if not settings.PRE_REG:
        return True
    try:
        if request.session['skater']:
            return True
        else:
            return False
    except KeyError:
        return False


# STEP ZERO
# Pre-load skater details for pre-registered person.
def load_pre_reg(request):
    pass



# STEP ONE
# Personal information - Name, address
def personal_details(request):
    #if not can_pre_reg:
    #return render(request, 'registration/pre-reg-only-sorry.html', {})

    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            request.session['personal_details'] = form
            return HttpResponseRedirect(reverse('registration.views.emergency_info'))
    else:
        try:
            form = request.session['personal_details']
        except KeyError:
            form = PersonalForm()

    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 1, 'step_info': 'Skater Information', })
    

# STEP TWO
# Medical / emergency information
def emergency_info(request):
    if not can_pre_reg:
        return render(request, 'registration/pre-reg-only-sorry.html', {})

    try:
        request.session['personal_details']
    except KeyError:
        return HttpResponseRedirect(reverse('registration.views.personal_details'))

    if request.method == 'POST':
        form = EmergencyForm(request.POST)
        if form.is_valid():
            request.session['emergency_info'] = form
            return HttpResponseRedirect(reverse('registration.views.legal_stuff'))
    else:
        try:
            form = request.session['emergency_info']
        except KeyError:
            form = EmergencyForm()

    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 2, 'step_info': 'Emergency Contact and Medical Info', })



# STEP THREE
# Legal shit
def legal_stuff(request):
    if not can_pre_reg:
        return render(request, 'registration/pre-reg-only-sorry.html', {})
    
    try:
        request.session['personal_details']
        request.session['emergency_info']
    except KeyError:
        return HttpResponseRedirect(reverse('registration.views.emergency_info'))

    mwd_binder = LegalDocumentBinder.objects.get(short_name__exact = "mwd")
    if mwd_binder:
        text = {'mwd': mwd_binder.get_active_version_text()}
    else:
        text = {'mwd': 'Legal document not found in backend.....'}
    

    if request.method == 'POST':
        form = LegalForm(request.POST)
        if form.is_valid():
            request.session['legal_stuff'] = form
            return HttpResponseRedirect(reverse('registration.views.payment'))
    
    form = LegalForm(initial=text)

    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 3, 'step_info': 'Legal', })


# STEP FOUR
# Payment
def payment(request):
    if not can_pre_reg:
        return render(request, 'registration/pre-reg-only-sorry.html', {})
    
    try:
        request.session['personal_details']
        request.session['emergency_info']
        request.session['legal_stuff']
    except KeyError:
        return HttpResponseRedirect(reverse('registration.views.emergency_info'))
    
    data = { 'step_info': 'Dues Payment',
             'REGISTRATION_DEADLINE' : settings.REGISTRATION_DEADLINE,
             'REGISTRATION_PIP_INSTRUCTIONS' : settings.REGISTRATION_PIP_INSTRUCTIONS, 
             'REGISTRATION_MAIL_INSTRUCTIONS' : settings.REGISTRATION_MAIL_INSTRUCTIONS, 
             'STRIPE_PUBLISHABLE' : settings.STRIPE_PUBLISHABLE, }

    if request.method == 'POST':
        create_account = False
        form = PaymentForm(request.POST)
        if form.is_valid():
            # If the payment fails, don't create the account.
            create_account = True
            payment_method = form.cleaned_data['payment_method']
            if payment_method == 'cc':
                """ process credit card form """
                create_account = False
                data["cc_error"] = "Could not change your card"

            if create_account:
                if request.session.get("skater"):
                    pass

                # Here we'll actually create the account if it's a new one:
                else:
                    personal_data = request.session['personal_details'].cleaned_data
                    emergency_data = request.session['emergency_info'].cleaned_data
                    legal_data = request.session['legal_stuff'].cleaned_data
                    
                    skater = Skater.objects.create_user(personal_data['email'], "skates")
                    
                    skater.first_name = personal_data['first_name']
                    skater.last_name = personal_data['last_name']
                    skater.derby_name = personal_data['derby_name']
                    skater.derby_number = personal_data['derby_number']
                    skater.address1 = personal_data['address1']
                    skater.address2 = personal_data['address2']
                    skater.city = personal_data['city']
                    skater.state = personal_data['state']
                    skater.zip = personal_data['zip']
                    skater.phone = personal_data['phone']

                    skater.emergency_contact = emergency_data['emergency_contact']
                    skater.emergency_relationship = emergency_data['emergency_relationship']
                    skater.emergency_phone = emergency_data['emergency_phone']
                    skater.insurance_provider = emergency_data['insurance_company']
                    skater.hospital = emergency_data['hospital_preference']
                    skater.medical_details = emergency_data['allergies']

                    skater.save()

                    "Save legal signature"
                    mwd_binder = LegalDocumentBinder.objects.get(short_name__exact = "mwd")
                    if mwd_binder:
                        document = mwd_binder.get_active_version()
                        if document:
                            sig = LegalDocumentSignature(user=skater, document=document, ip=get_client_ip(request))
                            sig.save()
                        "else:"
                        "ERROR: No active document version."
                    "else:"
                    "ERROR: No binder with that name."
                    

                    "Create Invoice"
                    "Get registration skate session"
                    skate_session = SkateSession.objects.get(name__exact = settings.REGISTRATION_SESSION_NAME)
                    if skate_session:
                        "Get the first billing date for this session"
                        billing_period = SkateSessionPaymentSchedule.objects.filter(session=skate_session)
                        #if billing_period:
                        #    "Billing period is sorted automatically by date. Create an invoice attached to these attributes."
                        #    #invoice = billing_period.generate_invoice(skater)
                        #    #if paid by credit card:
                        #    #    invoice.paid()
                    "else:"
                    "ERROR: No session matches REGISTRATION_SESSION_NAME"

                    registered_skater = Skater.objects.get(pk=skater.id)
                    
                    send_registration_email(skate_session, registered_skater)

                    #request.session.flush()

                    return HttpResponseRedirect(reverse('registration.views.done'))
                    
        else:
            "Invalid form - form.is_valid() failed"
            data["error"] = "Could not create your account for some reason.... Try again and email us if it doesn't work."

        if create_account:
            pass


    return render(request, 'registration/payment-registration-form.html', data )
    

def done(request):
    return render(request, 'registration/done.html', {} )
