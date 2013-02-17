from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rink.forms import PaymentForm, AutopayForm, ProcessForm
from mwd import settings
from accounts.models import PaymentError, Invoice, Receipt, SkateSessionPaymentSchedule
from datetime import date
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

@login_required
def index(request):
    return HttpResponseRedirect(reverse('rink.views.dues'))
    #return render(request, 'rink/index.html')

@login_required
def dues(request):

    """ Pull in the card description if we haven't already tried to to do this. """
    try: 
        if request.user.stripe_customer_id != '' and (request.user.stripe_card_description is None or request.user.stripe_card_description == ''):
            request.user.update_stripe_card_description()
    except PaymentError:
        pass

    upcoming = SkateSessionPaymentSchedule.objects.filter(due_date__gte=date.today())
    invoices = Invoice.objects.filter(skater=request.user)
    payments = Receipt.objects.filter(skater=request.user)

    data = {
        "upcoming": upcoming,
        "invoices": invoices,
        "payments": payments,
        "message": request.session.get("payment_message"),
        "error": request.session.get("payment_error"),
    }

    if request.session.get("payment_message"):
        del request.session['payment_message']
    if request.session.get("payment_error"):
        del request.session['payment_error']

    return render(request, 'rink/dues.html', data)

""" Set automatic payment preferences """
@login_required
def autopay_dues(request):
    if request.method == 'POST':
        form = AutopayForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['autobill'] == 0:
                request.user.automatic_billing = False;
                request.session["payment_message"] = "<strong>Automatic payments disabled.</strong> Your card will not be billed automatically."
            elif form.cleaned_data['autobill'] == 1: 
                request.user.automatic_billing = True;
                request.session["payment_message"] = "<strong>Automatic payments enabled.</strong> Your card will be billed dues automatically on the due date."

            request.user.save()

    return HttpResponseRedirect(reverse('rink.views.dues'))


""" Process a dues payment using a saved credit card """
@login_required
def process_dues(request):
    if request.method == 'POST':
        form = ProcessForm(request.POST)
        if form.is_valid():
            try:
                request.user.charge_credit_card(request.user.get_unpaid_invoices_description())
            except PaymentError, e:
                request.session["payment_error"] = "<strong>There was a problem charging your card.</strong> " + e.value

    return HttpResponseRedirect(reverse('rink.views.dues'))
    

""" Update credit card and attempt to charge it. """
@login_required
def pay_dues(request):
    
    data = { 
        'STRIPE_PUBLISHABLE' : settings.STRIPE_PUBLISHABLE, 
    }

    finished = False
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            request.user.automatic_billing = form.cleaned_data['autobill']
            request.user.save()
            try:
                bal = request.user.balance
                request.user.update_stripe_customer(form.cleaned_data['stripe_token'])
                request.user.charge_credit_card(request.user.get_unpaid_invoices_description())
                if bal == 0:
                    request.session["payment_message"] = "<strong>Credit card updated.</strong>"
                else:
                    request.session["payment_message"] = "<strong>Payment successful!</strong> A receipt has been emailed to you."

                return HttpResponseRedirect(reverse('rink.views.dues'))
            except PaymentError, e:
                data['error'] = e.value

    return render(request, 'rink/dues_pay.html', data)

@login_required
def profile(request):
    data = {
        'user_short_name': request.user.get_short_name(),
    }
    return render(request, 'rink/profile.html', data)

