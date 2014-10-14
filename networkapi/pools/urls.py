# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'networkapi.pools.views',
    url(r'^pools/$', 'pool_list'),
    url(r'^pools/insert/$', 'pool_insert'),
    url(r'^pools/list_healthchecks/$', 'healthcheck_list'),
    url(r'^pools/delete/$', 'delete'),
    url(r'^pools/getbypk/(?P<id_server_pool>[^/]+)/$', 'get_by_pk'),
    url(r'^pools/get_all_members/(?P<id_server_pool>[^/]+)/$', 'list_all_members_by_pool'),
    url(r'^pools/remove/$', 'remove'),
    url(r'^pools/edit/$', 'pool_edit'),
    url(r'^pools/get_equip_by_ip/(?P<id_ip>[^/]+)/$', 'get_equipamento_by_ip')
)
