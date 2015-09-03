# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('networkapi.api_network.views',
    url(r'^networkv4/$', 'list_networksIPv4'),
    url(r'^networkv6/$', 'list_networksIPv6'),
)
