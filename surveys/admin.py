from surveys.models import Survey, SurveyQuestion, SurveyAnswer, SurveyInvite, SurveyResponse, SurveyResponseAnswer
from django.contrib import admin

admin.site.register(Survey)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyAnswer)
admin.site.register(SurveyInvite)
admin.site.register(SurveyResponse)
admin.site.register(SurveyResponseAnswer)
