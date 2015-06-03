
from mwd import settings
from mwd.utilities import random_string

from accounts.models import PaymentError, Invoice, Receipt, SkateSessionPaymentSchedule, Skater, SkaterStatus
from rink.forms import PaymentForm, AutopayForm, ProcessForm, AdminSkaterStatusForm, AdminSkaterPaymentForm
from surveys.models import Survey, SurveyQuestion, SurveyAnswer, SurveyInvite, SurveyResponseAnswer, SurveyResponse

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from datetime import date, datetime

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
                data['payment_error'] = e.value
        else:
            data['payment_error'] = "There was a problem processing the payment form. This shouldn't happen. Try again and contact us if you still have a problem."

    return render(request, 'rink/dues_pay.html', data)

@login_required
def profile(request):
    data = {
        'user_short_name': request.user.get_short_name(),
    }
    return render(request, 'rink/profile.html', data)




"""
ADMIN TOOLS
"""

def get_paid_stats():
    data = {
        "num_paid": Skater.objects.filter(balance__lte=0).count(),
        "num_unpaid": Skater.objects.filter(balance__gt=0, automatic_billing__exact=0).count(),
        "num_autopay": Skater.objects.filter(automatic_billing__exact=1).count(),
        "num_all": Skater.objects.exclude(status__name__exact="inactive").count(),
    }

    return data
    
def get_filtered_skaters(status="all"):
    if status == "all":
        return Skater.objects.order_by("derby_name", "last_name").all()
    if status == "paid":
        return Skater.objects.filter(balance__lte=0).order_by("derby_name", "last_name").all()
    if status == "unpaid":
        return Skater.objects.filter(balance__gt=0, automatic_billing__exact=0).order_by("derby_name", "last_name").all()
    if status == "autopay":
        return Skater.objects.filter(automatic_billing__exact=1).order_by("derby_name", "last_name").all()
    return []

@login_required
def admin_tools(request):
    if not request.user.is_admin:
        return render(request, 'rink/access_denied.html')

    data = get_paid_stats()

    return render(request, 'rink/admin-tools.html', data)

@login_required
def billing_tools(request, billing_filter):
    if not request.user.is_admin:
        return render(request, 'rink/access_denied.html')

    data = get_paid_stats()

    if billing_filter is None:
        billing_filter = "unpaid"
    data["filter"] = billing_filter

    data["skaters"] = get_filtered_skaters(billing_filter)

    return render(request, 'rink/admin-billing-tools.html', data)

@login_required
def skater_tools(request, skater_id):
    if not request.user.is_admin:
        return render(request, 'rink/access_denied.html')
    
    try:
        skater = Skater.objects.get(pk=skater_id)
    except Skater.DoesNotExist:
        return render(request, 'rink/access_denied.html')
    
    if request.method == 'POST':
        form = AdminSkaterStatusForm(request.POST)
        if form.is_valid():
            try:
                new_status = SkaterStatus.objects.get(pk=form.cleaned_data["status"])
            except SkaterStatus.DoesNotExist:
                return render(request, 'rink/admin_error.html', {"error", "Skater Status does not appear to exist." })
                
            skater.status = new_status
            skater.save()
            request.session["success_message"] = "<b>Saved new status.</b>" 
            return HttpResponseRedirect(reverse('rink.views.skater_tools', kwargs={"skater_id": skater.id } ))
            

    data = {
        "skater": skater,
        "skater_statuses": SkaterStatus.objects.all(),
    }

    if request.session.get("success_message"):
        data["success_message"] = request.session.get("success_message")
        del request.session['success_message']
    
    if request.session.get("payment_success"):
        data["payment_success"] = request.session.get("payment_success")
        del request.session['payment_success']
    
    if request.session.get("payment_error"):
        data["payment_error"] = request.session.get("payment_error")
        del request.session['payment_error']

    return render(request, 'rink/admin-skater-tools.html', data)


@login_required
def skater_tools_payment(request, skater_id):
    if not request.user.is_admin:
        return render(request, 'rink/access_denied.html')
    
    try:
        skater = Skater.objects.get(pk=skater_id)
    except Skater.DoesNotExist:
        return render(request, 'rink/access_denied.html')
    
    if request.method == 'POST':
        form = AdminSkaterPaymentForm(request.POST)
        if form.is_valid():
            receipt = Receipt(
                    skater = skater,
                    amount = float(form.cleaned_data["amount"]),
                    fee = 0,
                    method = form.cleaned_data["method"],
                    method_detail = form.cleaned_data["notes"],
                    date = datetime.now(),
                )
            receipt.save()

            skater.balance = skater.balance - form.cleaned_data["amount"]
            skater.save()

            skater.set_unpaid_invoices_paid(form.cleaned_data["amount"]) 

            request.session["payment_success"] = "<b>Payment Received</b> - " + form.cleaned_data["method"] + " of $" + str(form.cleaned_data["amount"])
        else:
            request.session["payment_error"] = "<b>Invalid payment</b> - You may have missed something on the form. Please try again."

    return HttpResponseRedirect(reverse('rink.views.skater_tools', kwargs={"skater_id": skater.id } ))


@login_required
def survey_stats(request, slug):
    if not request.user.is_admin:
        return render(request, 'rink/access_denied.html')

    all_surveys = Survey.objects.all()

    if slug:
        try:
            survey = Survey.objects.get(slug_url=slug)
        except Survey.DoesNotExist:
            return render(request, 'rink/survey_stats.html', {'surveys': all_surveys, 'error': "That survey does not appear to exist." })
    else:
        return render(request, 'rink/survey_stats.html', {'surveys': all_surveys} )


    questions = SurveyQuestion.objects.filter(survey=survey).all().select_related()

    invites_sent = SurveyInvite.objects.filter(survey=survey).all()
    invites_responded = SurveyInvite.objects.filter(survey=survey, date_responded__isnull=False)
    invites_waiting = SurveyInvite.objects.filter(survey=survey, date_responded__isnull=True)

    invites_responded_percent = int((float(invites_responded.count()) / invites_sent.count()) * 100)

    comments = SurveyResponse.objects.filter(survey=survey).exclude(comment="").all()

    for question in questions:

        """
        Some questions don't have responses or votes, those won't show up in the aggregate functions.
        Manually smash the stats together with the list of votes/percent counts.
        """
        answers = []

        base_answers = SurveyAnswer.objects.filter(question=question).all()
        for answer in base_answers:
            answers.append({'answer': answer.answer, 'count': 0, 'percent': 0})

        """
        Now, check for fill-in answers. Add those to the answers dict.
        """
        responses = SurveyResponseAnswer.objects.filter(question=question)
        for response in responses:
            for answer in answers:
                if response.answer == answer["answer"]:
                    break
            else:
                answers.append({'answer': response.answer, 'count': 0, 'percent': 0})

        answers_count = SurveyResponseAnswer.objects.filter(question=question).values('answer').annotate(votes=Count('answer'))
        total_responses = responses.count()
        for answer_count in answers_count:
            answer_count["percent"] = int((float(answer_count["votes"]) / total_responses) * 100)

            for stats_answer in answers:
                if  stats_answer["answer"] == answer_count["answer"]:
                    stats_answer["count"] = answer_count["votes"]
                    stats_answer["percent"] =  answer_count["percent"]
                    
        question.response_answers = answers

    return render(request, 'rink/survey_stats.html', {
        'surveys': all_surveys, 
        'survey': survey,
        'questions': questions,
        'comments': comments,

        'invites_sent': invites_sent,
        'invites_responded': invites_responded,
        'invites_waiting': invites_waiting,
        'invites_responded_percent': invites_responded_percent,

        'tab': 'stats',
    })

    
@login_required
def survey_invite(request, slug):
    if not request.user.is_admin:
        return render(request, 'rink/access_denied.html')
    
    all_surveys = Survey.objects.all()

    if slug:
        try:
            survey = Survey.objects.get(slug_url=slug)
        except Survey.DoesNotExist:
            return render(request, 'rink/survey_stats.html', {'surveys': all_surveys, 'error': "That survey does not appear to exist." })
    else:
        return render(request, 'rink/survey_stats.html', {'surveys': all_surveys} )


    submit_message = False
    if request.method == "POST":
        invites = request.POST.getlist('invite')
        
        sent = 0
        failed = 0

        for invite in invites:
            try:
                sk = Skater.objects.get(pk=invite)

                survey_invite = SurveyInvite()
                survey_invite.user = sk
                survey_invite.survey = survey
                survey_invite.hash = random_string(32)
                survey_invite.date_sent = datetime.now()
                survey_invite.save()


                html = render_to_string('emails/survey_invite.html',
                            {
                                'skater': sk,
                                'skater_short_name': sk.get_short_name(),
                                'survey': survey,
                                'invite': survey_invite,
                            }
                )

                msg = EmailMultiAlternatives(
                            "Mad Wreckin' Dolls Voting - %s" % (survey),
                            html,
                            settings.FROM_EMAIL,
                            [ sk.email ],
                            [ settings.FROM_EMAIL ],
                            headers = {
                                'Reply-To' : settings.FROM_EMAIL,
                                'CC' : "finance@madwreckindolls.com",
                                'Content-Type' : 'text/html'
                            },
                )
                
                msg.content_subtype = "html"
                msg.send(fail_silently = False)

                sent = sent + 1

            except Skater.DoesNotExist:
                """ failed for some reason or another """
                failed = failed + 1

        submit_message = "Sent %s voting invites to selected members." % (sent)
        if failed > 0:
            submit_message = submit_message + "<br><br><storng>Failed to sent %s invites for whatever reason. Weird." % (failed)


    all_skaters = Skater.objects.exclude(status__name="inactive").all()
    invited = all_skaters.filter(survey_invite__survey=survey)
    not_invited = all_skaters.exclude(pk__in=invited)

    return render(request, 'rink/survey_invite.html', {
        'surveys': all_surveys,
        'survey': survey,
        'tab': 'invite',
        'submit_message': submit_message,

        'invited': invited,
        'not_invited': not_invited,
    })



