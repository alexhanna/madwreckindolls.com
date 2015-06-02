from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    
    # Homepage
    url(r'^$', 'frontpage.views.index'),
    url(r'^robots.txt$', 'frontpage.views.robotstxt'),
    url(r'^newsletter/', 'frontpage.views.newsletter'),

    # Skater management portal
    url(r'^rink/', include('rink.urls')),

    # Registration
    url(r'^registration/', include('registration.urls')),

    # Surveys
    url(r'^surveys/', include('surveys.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()