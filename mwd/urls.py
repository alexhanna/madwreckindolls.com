from django.conf.urls import patterns, include, url
from django.contrib import admin
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


    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
