from django.shortcuts import render
from surveys.models import SurveyInvite, SurveyQuestion, SurveyAnswer, SurveyResponse, SurveyResponseAnswer
from datetime import datetime
from django.utils import timezone



"""
Django doesn't handle multiple (of the same) custom form models all that easily,
so we'll handle the validation here for the form instead of in a FormSet or ModelForm as usual.
"""

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

	questions = SurveyQuestion.objects.filter(survey=invite.survey).select_related()
	anything_else = ""
	errors = False

	if request.method == "POST":
		try:
			anything_else = request.POST.get("anything_else")
		except:
			pass

		for question in questions:
			valid_answer = False
			answer_text = False
			custom_answer = ""
			try: 
				answer_text = request.POST.get("question%s" % (question.id))
				valid_answer = SurveyAnswer.objects.get(question=question, answer=answer_text).answer
			except:
				pass

			if not valid_answer and answer_text == "custom" and question.allow_write_in:
				try:
					custom_answer = request.POST.get("question%scustom" % (question.id))
					if custom_answer != "":
						valid_answer = "custom"

				except:
					pass

			if valid_answer:
				question.selected = valid_answer
				question.custom = custom_answer
			else:
				question.error = "dammit"
				errors = True

		if not errors:
			""" Hooray, save the response. """
			""" At some point we would upgrade this to use legitimate database transactions, but for now
			we'll just keep it simple and not do that. """
			invite.date_responded = datetime.now()
			invite.save()

			response = SurveyResponse()
			response.survey = invite.survey
			response.comment = anything_else
			response.save()

			for question in questions:
				response_answer = SurveyResponseAnswer()
				response_answer.response = response
				response_answer.question = question
				if question.selected == "custom":
					response_answer.answer = question.custom
				else:
					response_answer.answer = question.selected
				response_answer.save()

			return render(request, "surveys/thanks.html", {})



	return render(request, "surveys/survey.html", {
		'survey': invite.survey, 
		'questions': questions,
		'anything_else': anything_else, 
		'errors': errors,
	})



