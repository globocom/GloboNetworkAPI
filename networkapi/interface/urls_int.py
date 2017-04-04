# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.interface.resource.InterfaceEnvironmentResource import InterfaceEnvironmentResource
from networkapi.interface.resource.InterfaceGetSwRouterResource import InterfaceGetSwRouterResource

interface_get_sw_router_resource = InterfaceGetSwRouterResource()
interface_environment_resource = InterfaceEnvironmentResource()

urlpatterns = patterns(
    '',
    url(r'^getbyidequip/(?P<id_equipamento>[^/]+)/$', interface_get_sw_router_resource.handle_request,
        name='interface.get_sw_router'),
    url(r'^associar-ambiente[/]?$', interface_environment_resource.handle_request,
        name='interface.associar'),
    url(r'^get-env-by-interface/(?P<id_interface>[^/]+)[/]?$', interface_environment_resource.handle_request,
        name='interface.ambiente.get')
)
