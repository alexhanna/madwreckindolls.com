from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    
    # pre-reg only
    (r'^(?P<uid>\d)/(?P<hash>[a-zA-Z0-9]{32})$', 'registration.views.load_pre_reg'),
    
    (r'^emergency-info$', 'registration.views.emergency_info'),
    (r'^anything-else$', 'registration.views.anything_else'),
    (r'^legal-stuff$', 'registration.views.legal_stuff'),
    (r'^pay-dues$', 'registration.views.payment'),
    (r'^done$', 'registration.views.done'),
    
    (r'^$', 'registration.views.personal_details'),
)
