# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from networkapi.api_network.views import DHCPRelayIPv4ByPkView, DHCPRelayIPv6ByPkView, \
	DHCPRelayIPv4View, DHCPRelayIPv6View
'''
TODO (v4 and v6)
POST /api/network - allocate network
DELETE /api/vlan/ID - remove network
PUT /api/network/ID - modify network
'''

urlpatterns = patterns('networkapi.api_network.views',
    url(r'^networkv4/$', 'networksIPv4'),
    url(r'^networkv6/$', 'networksIPv6'),
    url(r'^networkv4/(?P<network_id>\d+)/$', 'networksIPv4_by_pk'),
    url(r'^networkv6/(?P<network_id>\d+)/$', 'networksIPv6_by_pk'),
	url(r'^networkv4/(?P<network_id>\d+)/equipments/$', 'networkIPv4_deploy'),
	url(r'^networkv6/(?P<network_id>\d+)/equipments/$', 'networkIPv6_deploy'),
	url(r'^dhcprelayv4/$', DHCPRelayIPv4View.as_view()),
	url(r'^dhcprelayv6/$', DHCPRelayIPv6View.as_view()),
	url(r'^dhcprelayv4/(?P<dhcprelay_id>\d+)/$', DHCPRelayIPv4ByPkView.as_view()),
	url(r'^dhcprelayv6/(?P<dhcprelay_id>\d+)/$', DHCPRelayIPv6ByPkView.as_view()),
)
