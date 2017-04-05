# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.interface.resource.InterfaceDisconnectResource import InterfaceDisconnectResource
from networkapi.interface.resource.InterfaceGetResource import InterfaceGetResource
from networkapi.interface.resource.InterfaceResource import InterfaceResource

interface_resource = InterfaceResource()
interface_get_resource = InterfaceGetResource()
interface_disconnect_resource = InterfaceDisconnectResource()

urlpatterns = patterns(
    '',
    url(r'^$', interface_resource.handle_request,
        name='interface.insert'),
    url(r'^(?P<id_interface>[^/]+)/$', interface_resource.handle_request,
        name='interface.update.remove.by.pk'),
    url(r'^(?P<id_interface>[^/]+)/get/$', interface_get_resource.handle_request,
        name='interface.get.by.pk'),
    url(r'^get/(?P<channel_name>[^/]+)/(?P<id_equipamento>[^/]+)[/]?$', interface_get_resource.handle_request,
        name='interface.list.by.equip'),
    url(r'^get-by-channel/(?P<channel_name>[^/]+)/(?P<equip_name>[^/]+)[/]/?$', interface_get_resource.handle_request,
        name='interface.get.by.pk'),
    url(r'^equipamento/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request,
        name='interface.search.by.equipment'),
    url(r'^equipment/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, {'new': True},
        name='interface.search.by.equipment.new'),
    url(r'^(?P<id_interface>[^/]+)/(?P<back_or_front>[^/]+)/$', interface_disconnect_resource.handle_request,
        name='interface.remove.connection'),
    url(r'^(?P<nome_interface>.+?)/equipamento/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request,
        name='interface.search.by.interface.equipment'),
    url(r'^(?P<nome_interface>.+?)/equipment/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, {'new': True},
        name='interface.search.by.interface.equipment.new')
)
