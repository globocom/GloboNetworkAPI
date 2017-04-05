# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ambiente.resource.EnvironmentVipResource import EnvironmentVipResource
from networkapi.ambiente.resource.EnvironmentVipSearchResource import EnvironmentVipSearchResource
from networkapi.ambiente.resource.RequestAllVipsEnviromentVipResource import RequestAllVipsEnviromentVipResource

environment_vip_resource = EnvironmentVipResource()
environment_vip_search_resource = EnvironmentVipSearchResource()
environment_vip_search_all_vips_resource = RequestAllVipsEnviromentVipResource()

urlpatterns = patterns(
    '',
    url(r'^$', environment_vip_resource.handle_request,
        name='environment.vip.add'),
    url(r'^all/', environment_vip_resource.handle_request,
        name='environment.vip.all'),
    url(r'^search/$', environment_vip_search_resource.handle_request,
        name='environment.vip.search'),
    url(r'^search/(?P<id_vlan>[^/]+)/$', environment_vip_search_resource.handle_request,
        name='environment.vip.search'),
    url(r'^(?P<id_environment_vip>[^/]+)/$', environment_vip_resource.handle_request,
        name='environment.vip.update.remove'),
    url(r'^(?P<id_environment_vip>[^/]+)/vip/all/$', environment_vip_search_all_vips_resource.handle_request,
        name='environmentvip.vips.all')
)
