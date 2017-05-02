# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from networkapi.api_rack.views import RackView, RackDeployView, DataCenterView, DataCenterRoomsView, RackConfigView
from networkapi.api_rack.facade import available_rack_number


urlpatterns = patterns('',
    url(r'^rack/(?P<rack_id>\d+)/equipments/$', RackDeployView.as_view()),
    url(r'^rack/$', RackView.as_view()),
    url(r'^rack/config/$', RackConfigView.as_view()),
    url(r'^rack/environmentvlan/(?P<rack_id>\d+)/$', RackEnvironmentView.as_view()),
    url(r'^rack/list/all/$', RackView.as_view()),
    url(r'^rack/next/', available_rack_number),

    url(r'^dc/$', DataCenterView.as_view()),
    url(r'^dcrooms/$', DataCenterRoomsView.as_view()),
    url(r'^dcrooms/(?P<dcroom_id>\d+)/$', DataCenterRoomsView.as_view()),

)