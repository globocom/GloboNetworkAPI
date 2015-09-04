# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

'''
GET /api/network - lista redes
POST /api/network - aloca rede
GET /api/vlan/ID - lista rede
DELETE /api/vlan/ID - remove rede
PUT /api/network/ID - modifica cadastro rede

POST /api/network/ID/equipments - deploy config rede (L3) no switch
DELETE /api/network/ID/equipments - remove config rede (L3) no switch
'''

urlpatterns = patterns('networkapi.api_network.views',
    url(r'^networkv4/$', 'networksIPv4'),
    url(r'^networkv6/$', 'networksIPv6'),
	url(r'^networkv4/(?P<network_id>\d+)/equipments/$', 'networkIPv4_deploy'),
	url(r'^networkv6/(?P<network_id>\d+)/equipments/$', 'networkIPv6_deploy'),

)
