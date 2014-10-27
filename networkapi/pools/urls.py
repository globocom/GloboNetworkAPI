# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'networkapi.pools.views',
    url(r'^pools/$', 'pool_list'),
    url(r'^pools/insert/$', 'pool_insert'),
    url(r'^pools/list_healthchecks/$', 'healthcheck_list'),
    url(r'^pools/delete/$', 'delete'),
    url(r'^pools/remove/$', 'remove'),
    url(r'^pools/create/$', 'create'),
    url(r'^pools/getbypk/(?P<id_server_pool>[^/]+)/$', 'get_by_pk'),
    url(r'^pools/get_all_members/(?P<id_server_pool>[^/]+)/$', 'list_all_members_by_pool'),
    url(r'^pools/edit/$', 'pool_edit'),
    url(r'^pools/get_equip_by_ip/(?P<id_ip>[^/]+)/$', 'get_equipamento_by_ip'),
    url(r'^pools/enable/$', 'enable'),
    url(r'^pools/disable/$', 'disable'),
    url(r'^pools/get_opcoes_pool_by_ambiente/$', 'get_opcoes_pool_by_ambiente'),
    url(r'^pools/get_requisicoes_vip_by_pool/(?P<id_server_pool>[^/]+)/$', 'get_requisicoes_vip_by_pool'),
    url(r'^pools/list/by/environment/(?P<environment_id>[^/]+)/$', 'list_by_environment'),
    url(r'^pools/list/members/(?P<pool_id>[^/]+)/$', 'list_pool_members'),
    url(r'^pools/list/by/environment/vip/(?P<environment_vip_id>\d+)/$', 'list_by_environment_vip'),
)
