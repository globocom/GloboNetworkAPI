# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from networkapi.api_rack.views import RackView, RackDeployView


urlpatterns = patterns('',
    url(r'^rack/(?P<rack_id>\d+)/equipments/$', RackDeployView.as_view()),
    url(r'^rack/$', RackView.as_view()),
)