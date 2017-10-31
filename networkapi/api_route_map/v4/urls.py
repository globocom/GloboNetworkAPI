# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_route_map.v4 import views

urlpatterns = patterns(
    '',
    url(r'^route-map-entry/((?P<obj_ids>[;\w]+)/)?$',
        views.RouteMapEntryDBView.as_view()),
    url(r'^route-map/((?P<obj_ids>[;\w]+)/)?$',
        views.RouteMapDBView.as_view()),

)
