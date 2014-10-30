# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'networkapi.api_healthcheck.views',
    url(r'^healthcheck/insert/$', 'insert'),
)
