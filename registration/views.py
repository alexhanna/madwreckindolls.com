from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from registration.forms import PersonalForm, EmergencyForm, LegalForm, PaymentForm
from legal_headache.models import LegalDocumentBinder, LegalDocument
from mwd import settings


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
    if not can_pre_reg:
        return render(request, 'registration/pre-reg-only-sorry.html', {})

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
                if request.session['skater']:
                    pass

                # Here we'll actually create the account if it's a new one:
                else:
                    user = User.objects.create_user(email, email, password)
                    user


        else:
            data["error"] = "Could not create your account for some reason.... Try again and email us if it doesn't work."

        if create_account:
            pass


    return render(request, 'registration/payment-registration-form.html', data )
    

