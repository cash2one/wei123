from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^weixin/admin/', include(admin.site.urls)),
    url(r'^weixin/', include('weisite.urls')),
)
