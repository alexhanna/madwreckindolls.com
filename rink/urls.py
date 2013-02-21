from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
                       
                       
""" Auth URL configuration stuff is heavily borrowed from: 
    http://peyman-django.blogspot.com/2010/03/full-easy-authentication-using_19.html """


urlpatterns = patterns('',
                       (r'^$', 'rink.views.index'),
                       (r'^dues/$', 'rink.views.dues'),
                       (r'^dues/pay$', 'rink.views.pay_dues'),
                       (r'^dues/autopay$', 'rink.views.autopay_dues'),
                       (r'^dues/process-dues$', 'rink.views.process_dues'),
                       (r'^profile$', 'rink.views.profile'),

                       (r'^admin-tools$', 'rink.views.admin_tools'),
                       (r'^admin-tools/billing/(?P<billing_filter>all|paid|unpaid|autopay)?$', 'rink.views.billing_tools'),
                       (r'^admin-tools/skaters/(?P<skater_id>\d+)$', 'rink.views.skater_tools'),

                       (r'^login/$', 
                        'django.contrib.auth.views.login', 
                        {'template_name': 'rink/login.html'}),

                       (r'^logout/$', 
                        'django.contrib.auth.views.logout', 
                        {'template_name': 'rink/logout.html'}),

                       (r'^password-change/$', 
                        'django.contrib.auth.views.password_change', 
                        {'template_name': 'rink/password_change_form.html'}),

                       (r'^password-change/done/$', 
                        'django.contrib.auth.views.password_change_done', 
                        {'template_name': 'rink/password_change_done.html'}),

                       (r'^password-reset/$', 
                        'django.contrib.auth.views.password_reset', 
                        {'template_name': 'rink/password_reset_form.html',
                         'email_template_name': 'emails/password_reset_email.html'}),

                       (r'^password-reset/done/$', 
                        'django.contrib.auth.views.password_reset_done', 
                        {'template_name': 'rink/password_reset_done.html'}),

                       (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
                        'django.contrib.auth.views.password_reset_confirm', 
                        {'template_name': 'rink/password_reset_confirm.html'}),

                       (r'^reset/done/$', 
                        'django.contrib.auth.views.password_reset_complete', 
                        {'template_name': 'rink/password_reset_complete.html'}),


)
