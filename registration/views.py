from django.shortcuts import render
from registration.forms import PersonalForm, EmergencyForm, LegalForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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

    return render(request, 'registration/basic-registration-form.html', { 'form': form, })
    

# STEP TWO
# Medical / emergency information
def emergency_info(request):
    if request.method == 'POST':
        form = EmergencyForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('registration.views.legal_stuff'))
    else:
        form = EmergencyForm()

    return render(request, 'registration/basic-registration-form.html', { 'form': form, })



# STEP THREE
# Legal shit
def legal_stuff(request):
    if request.method == 'POST':
        form = LegalForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('registration.views.payment'))
    else:
        form = LegalForm()

    return render(request, 'registration/basic-registration-form.html', { 'form': form, })


# STEP FOUR
# Payment
def payment(request):
    pass
