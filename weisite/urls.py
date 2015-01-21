from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^home/',      'weisite.views.home'),
)
