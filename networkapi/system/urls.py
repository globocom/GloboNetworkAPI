# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('networkapi.system.views',
    url(r'^system/variables/save', 'save'),
)