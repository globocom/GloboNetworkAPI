# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.vlan.resource.NetworkTypeResource import NetworkTypeResource

network_type_resource = NetworkTypeResource()

urlpatterns = patterns(
    '',
    url(r'^$', network_type_resource.handle_request,
        name='network_type.insert.search'),
    url(r'^(?P<id_net_type>[^/]+)/$', network_type_resource.handle_request,
        name='network_type.update.remove.by.pk')
)
