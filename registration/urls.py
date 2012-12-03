from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^done$', TemplateView.as_view(template_name="registration/done.html") ),
    (r'^emergency-info$', 'registration.views.emergency_info'),
    (r'^legal-stuff$', 'registration.views.legal_stuff'),
    (r'^pay-dues$', 'registration.views.payment'),
    (r'^$', 'registration.views.personal_details'),
)
