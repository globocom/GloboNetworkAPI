# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('networkapi.system.views',
    url(r'^system/variables/save/$', 'save'),
    url(r'^system/variables/list/$', 'get_all'),
    url(r'system/variables/delete/(?P<variable_id>[^/]+)/$', 'delete'),
)