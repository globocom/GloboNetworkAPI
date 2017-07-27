# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from networkapi.api_rack import views as rack_views
from networkapi.api_rack import facade as rack_facade


from networkapi.api_rack.views import RackDeployView
from networkapi.api_rack.views import RackView

urlpatterns = patterns('',
    url(r'^rack/(?P<rack_id>\d+)/equipments/$', rack_views.RackDeployView.as_view()),
    url(r'^rack/fabric/(?P<fabric_id>\d+)[/]$', rack_views.RackView.as_view()),
    url(r'^rack/$', rack_views.RackView.as_view()),
    url(r'^rack/(?P<rack_id>\d+)/$', rack_views.RackView.as_view()),
    url(r'^rack/config/(?P<rack_id>\d+)/$', rack_views.RackConfigView.as_view()),
    url(r'^rack/environmentvlan/(?P<rack_id>\d+)/$', rack_views.RackEnvironmentView.as_view()),
    url(r'^rack/list/all/$', rack_views.RackView.as_view()),
    url(r'^rack/next/', rack_facade.available_rack_number),

    url(r'^dc/$', rack_views.DataCenterView.as_view()),
    url(r'^dcrooms/$', rack_views.FabricView.as_view()),
    url(r'^dcrooms/id/(?P<fabric_id>\d+)/$', rack_views.FabricView.as_view()),
    url(r'^dcrooms/name/(?P<fabric_name>\s+)/$', rack_views.FabricView.as_view()),
    url(r'^dcrooms/dc/(?P<dc_id>\d+)/$', rack_views.FabricView.as_view()),

)

