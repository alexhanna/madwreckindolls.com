from django.shortcuts import render
from surveys.models import SurveyInvite
from datetime import datetime
from django.utils import timezone

def survey(request, slug, invite_hash):
	error = False
	try:
		invite = SurveyInvite.objects.get(survey__slug_url=slug, hash__exact=invite_hash)
	except SurveyInvite.DoesNotExist:
		error = "Survey not found."
	else: 
		if invite.responded():
			error = "It appears you already responded to this survey."
		elif invite.survey.start_date and invite.survey.start_date > timezone.now():
			error = "This survey has not opened up for responses quite yet. Check back later."
		elif invite.survey.end_date < timezone.now():
			error = "This survey has been closed to new responses."

	if error:
		return render(request, "surveys/error.html", {"error": error} )


	return render(request, "surveys/survey.html", {} )



