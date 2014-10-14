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
    url(r'^pools/remove/$', 'remove'),
)
