# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_ip import views

urlpatterns = patterns(
    '',
    url(r'^v3/ipv4/async/((?P<obj_ids>[;\w]+)/)?$',
        views.IPv4AsyncView.as_view()),
    url(r'^v3/ipv6/async/((?P<obj_ids>[;\w]+)/)?$',
        views.IPv6AsyncView.as_view()),
    url(r'^v3/ipv4/((?P<obj_ids>[;\w]+)/)?$', views.IPv4View.as_view()),
    url(r'^v3/ipv6/((?P<obj_ids>[;\w]+)/)?$', views.IPv6View.as_view()),
)
