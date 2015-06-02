from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
	(r'^(?P<slug>[-\w\d]+)/(?P<invite_hash>[a-zA-Z0-9]{32})$', 'surveys.views.survey'),
)
