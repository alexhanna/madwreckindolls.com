from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from registration.forms import PersonalForm, EmergencyForm, LegalForm
from legal_headache.models import LegalDocumentBinder, LegalDocument
from mwd import settings


# STEP ONE
# Personal information - Name, address
def personal_details(request):
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
    mwd_binder = LegalDocumentBinder.objects.get(short_name__exact = "mwd")
    if mwd_binder:
        text = {'mwd': mwd_binder.get_active_version_text()}
    else:
        text = {'mwd': 'Legal document not found in backend.....'}
    

    if request.method == 'POST':
        form = LegalForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('registration.views.payment'))
    
    form = LegalForm(initial=text)

    return render(request, 'registration/basic-registration-form.html', { 'form': form, 'step': 3, 'step_info': 'Legal', })


# STEP FOUR
# Payment
def payment(request):

    data = { 'step_info': 'Dues Payment',
             'REGISTRATION_DEADLINE' : settings.REGISTRATION_DEADLINE,
             'REGISTRATION_PIP_INSTRUCTIONS' : settings.REGISTRATION_PIP_INSTRUCTIONS, 
             'REGISTRATION_MAIL_INSTRUCTIONS' : settings.REGISTRATION_MAIL_INSTRUCTIONS, }

    return render(request, 'registration/payment-registration-form.html', data )
    

