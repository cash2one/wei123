from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^home/',      'weisite.views.home'),
    url(r'^collect/',   'weisite.views.collect'),
    url(r'^clean/',     'weisite.views.clean'),
    url(r'^subscriber/',     'weisite.views.subscriber'),
    url(r'^google/',     'weisite.views.google'),
)
