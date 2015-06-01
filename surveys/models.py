from django.db import models
from accounts.models import Skater

class Survey(models.Model):    
    name = models.CharField(max_length=50, help_text="Name of this Survey")
    description = models.TextField(help_text="Description of this survey to the members.")
    slug_url = models.SlugField()
    created_date = models.DateTimeField(auto_now_add=True, help_text="Survey Creation Date")
    start_date = models.DateTimeField(help_text="Start date for this survey")
    end_date = models.DateTimeField(help_text="End date for this survey")

	def __unicode__(self):
        return self.name


class SurveyQuestion(models.Model):
	survey = models.ForeignKey(Survey, related_name="question")
	question = models.TextField()
	allow_write_in = models.BooleanField(default=False)
	allow_comment = models.BooleanField(default=False)

	def __unicode__(self):
		return self.question


class SurveyInvite(models.Model):
	user = models.ForeignKey(Skater, related_name="survey_invite")
	survey = models.ForeignKey(Survey, related_name="survey_invite")
	hash = models.TextField(max_length=32)
	date_sent = models.DateTimeField(auto_now_add=True)
	date_responded = models.DateTimeField(blank=True, null=True)

	def responded(self):
		if self.date_responded:
			return True
		return False

	def __unicode__(self):
		return "%s" % (self.user.email)


class SurveyResponse(models.Model):
	survey = models.ForeignKey(Survey, related_name="response")
	comment = models.TextField(blank=True)

	def __unicode__(self):
		return "Response to %s" % (self.survey.name)


class SurveyResponseAnswer(models.Model):
	response = models.ForeignKey(SurveyResponse, related_name="answer")
	question = models.ForeignKey(SurveyQuestion, related_name="answer")
	answer = models.TextField(blank=True)

	def __unicode__(self):
		return "Answer: %s" % (self.answer)





