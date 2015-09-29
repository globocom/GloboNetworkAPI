# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

'''
TODO (v4 and v6)
GET /api/network - list networks
POST /api/network - allocate network
GET /api/vlan/ID - list network
DELETE /api/vlan/ID - remove network
PUT /api/network/ID - modify network

POST /api/network/ID/equipments - deploy config (L3) on switches
DELETE /api/network/ID/equipments - remove config (L3) from switches
'''

urlpatterns = patterns('networkapi.api_network.views',
    url(r'^networkv4/$', 'networksIPv4'),
    url(r'^networkv6/$', 'networksIPv6'),
    url(r'^networkv4/(?P<network_id>\d+)/$', 'networksIPv4_by_pk'),
    url(r'^networkv6/(?P<network_id>\d+)/$', 'networksIPv6_by_pk'),
	url(r'^networkv4/(?P<network_id>\d+)/equipments/$', 'networkIPv4_deploy'),
	url(r'^networkv6/(?P<network_id>\d+)/equipments/$', 'networkIPv6_deploy'),

)
