from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^home/',      'weisite.views.home'),
    url(r'^poster/',    'weisite.views.poster'),
    url(r'^collect/',   'weisite.views.collect'),
    url(r'^clean/',     'weisite.views.clean'),
    url(r'^subscriber/',     'weisite.views.subscriber'),
    url(r'^google/',    'weisite.views.google'),
    url(r'^key',       'weisite.views.weixin_log'),
    url(r'^full/',      'weisite.views.full_log'),
)
