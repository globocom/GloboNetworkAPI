# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_neighbor.v4 import views

urlpatterns = patterns(
    '',
    url(r'^neighborv4/deploy/((?P<obj_ids>[;\w]+)/)?$',
        views.NeighborV4DeployView.as_view()),
    url(r'^neighborv4/((?P<obj_ids>[;\w]+)/)?$',
        views.NeighborV4DBView.as_view()),
    url(r'^neighborv6/deploy/((?P<obj_ids>[;\w]+)/)?$',
        views.NeighborV6DeployView.as_view()),
    url(r'^neighborv6/((?P<obj_ids>[;\w]+)/)?$',
        views.NeighborV6DBView.as_view()),
)
