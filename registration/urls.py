from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    
    # pre-reg only
    (r'^(?P<uid>\d)/(?P<hash>[a-z0-9]{32})$', 'registration.views.load_pre_reg'),
    
    (r'^emergency-info$', 'registration.views.emergency_info'),
    #(r'^legal-stuff$', 'registration.views.legal_stuff'),
    (r'^pay-dues$', 'registration.views.payment'),
    (r'^done$', TemplateView.as_view(template_name="registration/done.html") ),
    
    (r'^$', 'registration.views.personal_details'),
)
