from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^home/',      'weisite.views.home'),
    url(r'^collect/',   'weisite.views.collect'),
    url(r'^clean/',     'weisite.views.clean'),
)
