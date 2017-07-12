# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from networkapi.api_ip.v4 import views

urlpatterns = patterns(
    '',
    url(r'^ipv4/async/((?P<obj_ids>[;\w]+)/)?$',
        views.IPv4V4AsyncView.as_view()),
    url(r'^ipv6/async/((?P<obj_ids>[;\w]+)/)?$',
        views.IPv6V4AsyncView.as_view()),
    url(r'^ipv4/((?P<obj_ids>[;\w]+)/)?$', views.IPv4V4View.as_view()),
    url(r'^ipv6/((?P<obj_ids>[;\w]+)/)?$', views.IPv6V4View.as_view()),
    url(r'^ipv6/((?P<obj_ids>[;\w]+)/)?$', views.IPv6V4View.as_view()),

)
