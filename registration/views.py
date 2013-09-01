from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from accounts.models import Skater, SkaterStatus, SkateSession, SkateSessionPaymentSchedule, Invoice, Receipt, PaymentError, generate_scheduled_invoice
from registration.forms import PersonalForm, EmergencyForm, LegalForm, PaymentForm, AnythingElseForm
from registration.email import send_registration_email
from legal.models import LegalDocumentBinder, LegalDocument, LegalDocumentSignature
from mwd import settings
from mwd.utilities import get_client_ip
from django.db import IntegrityError

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
def load_pre_reg(request, uid = False, hash = False):

    data = {
        'mailto' : settings.FROM_EMAIL
    }

    if not uid or not hash:
        return render(request, 'registration/pre-reg-only-sorry.html', data)

    try:
        skater = Skater.objects.get(pk=uid)
    except Skater.DoesNotExist:
        return render(request, 'registration/pre-reg-problem.html', data)

    """ MD5 will be their password hash and the email address concatonated """
    if skater.user_hash != hash:
        return render(request, 'registration/pre-reg-problem.html', data)

    """ Payment preference should already be set if the user is registered. """
    if skater.registration_completed:
        return render(request, 'registration/pre-reg-already-registered.html', data)

    """ Things seem fine, load them up and point them towards registration. """
    request.session['skater'] = skater
    return HttpResponseRedirect(reverse('registration.views.personal_details'))
     



# STEP ONE
# Personal information - Name, address
def personal_details(request):
    if not can_pre_reg(request):
        return render(request, 'registration/pre-reg-only-sorry.html', { 'mailto' : settings.FROM_EMAIL })

    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            request.session['personal_details'] = form
            return HttpResponseRedirect(reverse('registration.views.emergency_info'))
    else:
        show_errors = True
        try:
            form = request.session['personal_details']
        except KeyError:
            show_errors = False
            try:
                skater = request.session['skater']
                initial_data = {
                    'derby_name': skater.derby_name,
                    'derby_number': skater.derby_number,
                    'first_name': skater.first_name,
                    'last_name': skater.last_name,
                    'address1': skater.address1,
                    'address2': skater.address2,
                    'city': skater.city,
                    'state': skater.state,
                    'zip': skater.zip,
                    'phone': skater.phone,
                    'email': skater.email,
		    'dob': skater.dob,
                    'previous_level': skater.last_level,
                }
            except KeyError:
                initial_data = {'state': 'WI'}
            form = PersonalForm(initial_data)
            form.helper.form_show_errors = show_errors

    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 1, 'step_info': 'Skater Information', })
    

# STEP TWO
# Medical / emergency information
def emergency_info(request):
    if not can_pre_reg(request):
        return render(request, 'registration/pre-reg-only-sorry.html', { 'mailto' : settings.FROM_EMAIL })

    try:
        request.session['personal_details']
    except KeyError:
        return HttpResponseRedirect(reverse('registration.views.personal_details'))
    
    show_errors = True

    if request.method == 'POST':
        form = EmergencyForm(request.POST)
        if form.is_valid():
            request.session['emergency_info'] = form
                    
            personal_data = request.session['personal_details'].cleaned_data
            emergency_data = request.session['emergency_info'].cleaned_data

            if request.session.get("skater"):
                "Previously created skater"
                skater = request.session.get("skater")
                # Make inactive skaters active now
                if skater.status == SkaterStatus.objects.get(name__exact = settings.REGISTRATION_INACTIVE_STATUS):
                    skater.status = SkaterStatus.objects.get(name__exact = settings.REGISTRATION_DEFAULT_STATUS)
            else:
                "Brand new registratered user"
                try:
		   skater = Skater.objects.create_user(personal_data['email'], Skater.objects.make_random_password())
                   skater.status = SkaterStatus.objects.get(name__exact = settings.REGISTRATION_DEFAULT_STATUS)
		except IntegrityError:
        	   return render(request, 'registration/reg-email-exists.html', { 'mailto' : settings.FROM_EMAIL })
		   
                    
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
            skater.dob = personal_data['dob']
            skater.last_level = personal_data['previous_level']
            skater.hope_level = personal_data['hope_level']

            skater.emergency_contact = emergency_data['emergency_contact']
            skater.emergency_relationship = emergency_data['emergency_relationship']
            skater.emergency_phone = emergency_data['emergency_phone']
            skater.wftda_number = emergency_data['wftda_number']
            skater.insurance_provider = emergency_data['insurance_company']
            skater.hospital = emergency_data['hospital_preference']
            skater.medical_details = emergency_data['allergies']
            skater.first_aid_certified = emergency_data['first_aid_certified']
            skater.first_aid_volunteer = emergency_data['first_aid_volunteer']

            skater.save()
    
            """Generate Invoice"""
            """ If dues amount is zero, just create an account. """
            dues_amount = False
            skate_session = SkateSession.objects.get(name__exact = settings.REGISTRATION_SESSION_NAME)
            if skate_session:
                billing_period = SkateSessionPaymentSchedule.objects.filter(session=skate_session)[0:1].get()
                if billing_period:
                    dues_amount = billing_period.get_dues_amount(status=skater.status)
                    invoice = generate_scheduled_invoice(skater, billing_period)
                    request.session['invoice'] = invoice

            """ Something isn't setup right (no valid skate session, no valid billing period) """
            if not dues_amount:
                dues_amount = 0
                """ Log/alert of an error here.... """ 
            
            """ Refresh skater session object after invoice generation (new balance) """
            request.session['skater'] = Skater.objects.get(pk=skater.id)

            return HttpResponseRedirect(reverse('registration.views.anything_else'))
    else:
        try:
            form = request.session['emergency_info']
        except KeyError:
            initial_data = {}
            show_errors = False
            try:
                skater = request.session['skater']
                if skater.wftda_number != "":
                    initial_data['wftda_number'] = skater.wftda_number
                    initial_data['wftda_confirm'] = 'yes'
                    initial_data['emergency_contact'] = skater.emergency_contact
                    initial_data['emergency_phone'] = skater.emergency_phone
                    initial_data['emergency_relationship'] = skater.emergency_relationship
                    initial_data['insurance_provider'] = skater.insurance_provider
                    initial_data['hosptial_preference'] = skater.hospital
                    initial_data['allergies'] = skater.medical_details
            except KeyError:
                pass
            form = EmergencyForm(initial_data)

    form.helper.form_show_errors = show_errors
    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 2, 'step_info': 'Emergency Contact and Medical Info', })


# STEP TWO POINT FIVE
# ANYTHING ELSE WE SHOULD KNOW?
def anything_else(request):
    if not can_pre_reg(request):
        return render(request, 'registration/pre-reg-only-sorry.html', { 'mailto' : settings.FROM_EMAIL })
    
    if not request.session.get("skater"):
        return HttpResponseRedirect(reverse('registration.views.emergency_info'))
    
    skater = Skater.objects.get(pk=request.session.get("skater").id)

    if request.method == 'POST':
        form = AnythingElseForm(request.POST)
        if form.is_valid():
            skater.anything_else_registration = form.cleaned_data['anything_else_registration']
            skater.save()
            return HttpResponseRedirect(reverse('registration.views.legal_stuff'))
    else:
        initial_data = { 'anything_else_registration':  skater.anything_else_registration }
        form = AnythingElseForm()
    
    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 3, 'step_info': 'Anything Else?', })


# STEP THREE
# Legal shit
def legal_stuff(request):
    if not can_pre_reg(request):
        return render(request, 'registration/pre-reg-only-sorry.html', { 'mailto' : settings.FROM_EMAIL })
    
    if not request.session.get("skater"):
        return HttpResponseRedirect(reverse('registration.views.emergency_info'))
    
    skater = Skater.objects.get(pk=request.session.get("skater").id)
            
    mwd_binder = LegalDocumentBinder.objects.get(short_name__exact = "mwd")
    if mwd_binder:
        document = mwd_binder.get_active_version()
        if document:
            text = {'mwd' : document.text }
        else:
            text = { 'mwd' : "Problem pulling legal document from backend...." }
    else:
        text = {'mwd': 'Legal document not found in backend.....'}
    
    # Check to see if they already signed it
    try:
        sig = LegalDocumentSignature.objects.get(document=document, user=skater)
        return HttpResponseRedirect(reverse('registration.views.payment'))
    except LegalDocumentSignature.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = LegalForm(request.POST)
        if form.is_valid():
            if document:
                sig = LegalDocumentSignature(
                                document = document,
                                user = skater,
                                ip = get_client_ip(request)
                      )
                sig.save()
            return HttpResponseRedirect(reverse('registration.views.payment'))
    
    form = LegalForm(initial=text)

    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 4, 'step_info': 'Legal', })





# STEP FOUR
# Payment
def payment(request):
    if not request.session.get("skater"):
        return HttpResponseRedirect(reverse('registration.views.emergency_info'))

    
    data = { 'step_info': 'Dues Payment',
             'REGISTRATION_DEADLINE' : settings.REGISTRATION_DEADLINE,
             'REGISTRATION_PIP_INSTRUCTIONS' : settings.REGISTRATION_PIP_INSTRUCTIONS, 
             'REGISTRATION_MAIL_INSTRUCTIONS' : settings.REGISTRATION_MAIL_INSTRUCTIONS, 
             'STRIPE_PUBLISHABLE' : settings.STRIPE_PUBLISHABLE, }
    
    skater = Skater.objects.get(pk=request.session.get("skater").id)
    
    try:
        invoice = request.session.get("invoice")
    except e:
        pass

    data["skater"] = skater

    payment_method = "pip"
    automatic_billing = False

    finished = False
    if skater.balance <= 0:
        finished = True
    elif request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            automatic_billing = form.cleaned_data['autobill']
            if payment_method == 'cc':
                """ process credit card form """
                payment_method = "credit"
                try:
                    skater.create_stripe_customer(form.cleaned_data['stripe_token'])
                    skater.charge_credit_card(invoice.description)
                    finished = True
                except PaymentError, e:
                    data['error'] = e.value
            else:
               finished = True
                    
        else:
            """Invalid form - form.is_valid() failed"""
            data["error"] = "Could not create your account for some reason.... Try again and email us if it doesn't work."

    if finished:
        if skater.balance <= 0:
            invoice.mark_paid()

        skater.registration_completed = True
        skater.payment_method = payment_method
        skater.automatic_billing = automatic_billing
        skater.save()

        try:
            skate_session = SkateSession.objects.get(name__exact = settings.REGISTRATION_SESSION_NAME)
            send_registration_email(skate_session, skater)
        except SkateSession.DoesNotExist:
            pass
            """ Handle error reporting here... """
    
        """ Clear out the session information """
        request.session.flush()
        request.session['email'] = skater.email
        request.session['balance'] = skater.balance

        return HttpResponseRedirect(reverse('registration.views.done'))
                    
    return render(request, 'registration/payment-registration-form.html', data )
    

def done(request):
    if not request.session.get("email"):
        return render(request, 'registration/pre-reg-problem.html', {} )

    return render(request, 'registration/done.html', {'email': request.session.get("email"), 'balance': request.session.get("balance"), 'FROM_EMAIL': settings.FROM_EMAIL } )
