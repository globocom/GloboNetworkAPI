# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.interface.resource.InterfaceChannelResource import InterfaceChannelResource

interface_channel_resource = InterfaceChannelResource()

urlpatterns = patterns(
    '',
    url(r'^editar[/]?$', interface_channel_resource.handle_request,
        name='channel.edit'),
    url(r'^inserir[/]?$', interface_channel_resource.handle_request,
        name='channel.add'),
    url(r'^delete/(?P<channel_name>[^/]+)/$', interface_channel_resource.handle_request,
        name='channel.delete'),
    # url(r'^get-by-name[/]?$', interface_channel_resource.handle_request,
    #     name='channel.get')
)
