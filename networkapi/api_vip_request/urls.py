# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'networkapi.api_vip_request.views',
    url(r'^vip/request/save/?(?P<pk>\d+)?/?$', 'save'),
    url(r'^vip/request/add/pools/$', 'add_pools'),
    url(r'^vip/request/delete/(?P<delete_pools>\d+)/$', 'delete'),
    url(r'^vip/list/environment/by/environment/vip/(?P<environment_vip_id>\d+)/$', 'list_environment_by_environment_vip'),
)
