# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_network.views import v3
from networkapi.api_network.views.v1 import DHCPRelayIPv4ByPkView
from networkapi.api_network.views.v1 import DHCPRelayIPv4View
from networkapi.api_network.views.v1 import DHCPRelayIPv6ByPkView
from networkapi.api_network.views.v1 import DHCPRelayIPv6View

urlpatterns = patterns(

    'networkapi.api_network.views.v1',
    url(r'^networkv4/$', 'networksIPv4'),
    url(r'^networkv6/$', 'networksIPv6'),
    url(r'^networkv4/(?P<network_id>\d+)/$', 'networksIPv4_by_pk'),
    url(r'^networkv6/(?P<network_id>\d+)/$', 'networksIPv6_by_pk'),
    url(r'^networkv4/(?P<network_id>\d+)/equipments/$', 'networkIPv4_deploy'),
    url(r'^networkv6/(?P<network_id>\d+)/equipments/$', 'networkIPv6_deploy'),
    url(r'^dhcprelayv4/$', DHCPRelayIPv4View.as_view()),
    url(r'^dhcprelayv6/$', DHCPRelayIPv6View.as_view()),
    url(r'^dhcprelayv4/(?P<dhcprelay_id>\d+)/$',
        DHCPRelayIPv4ByPkView.as_view()),
    url(r'^dhcprelayv6/(?P<dhcprelay_id>\d+)/$',
        DHCPRelayIPv6ByPkView.as_view()),

    ########################
    # Network V3
    ########################
    url(r'^v3/networkv4/deploy/async/((?P<obj_ids>[;\w]+)/)?$',
        v3.Networkv4DeployAsyncView.as_view()),
    url(r'^v3/networkv6/deploy/async/((?P<obj_ids>[;\w]+)/)?$',
        v3.Networkv6DeployAsyncView.as_view()),
    url(r'^v3/networkv4/async/((?P<obj_ids>[;\w]+)/)?$',
        v3.Networkv4AsyncView.as_view()),
    url(r'^v3/networkv6/async/((?P<obj_ids>[;\w]+)/)?$',
        v3.Networkv6AsyncView.as_view()),
    url(r'^v3/networkv4/force/((?P<obj_ids>[;\w]+)/)?$',
        v3.NetworkIPv4ForceView.as_view()),
    url(r'^v3/networkv6/force/((?P<obj_ids>[;\w]+)/)?$',
        v3.NetworkIPv6ForceView.as_view()),
    url(r'^v3/networkv4/deploy/((?P<obj_ids>[;\w]+)/)?$',
        v3.NetworkIPv4DeployView.as_view()),
    url(r'^v3/networkv6/deploy/((?P<obj_ids>[;\w]+)/)?$',
        v3.NetworkIPv6DeployView.as_view()),
    url(r'^v3/networkv4/((?P<obj_ids>[;\w]+)/)?$',
        v3.NetworkIPv4View.as_view()),
    url(r'^v3/networkv6/((?P<obj_ids>[;\w]+)/)?$',
        v3.NetworkIPv6View.as_view()),

)
