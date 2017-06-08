# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ip.resource.NetworkAddResource import NetworkAddResource
from networkapi.ip.resource.NetworkEditResource import NetworkEditResource
from networkapi.ip.resource.NetworkIPv4AddResource import NetworkIPv4AddResource
from networkapi.ip.resource.NetworkIPv4DeallocateResource import NetworkIPv4DeallocateResource
from networkapi.ip.resource.NetworkIPv4GetResource import NetworkIPv4GetResource
from networkapi.ip.resource.NetworkIPv6AddResource import NetworkIPv6AddResource
from networkapi.ip.resource.NetworkIPv6DeallocateResource import NetworkIPv6DeallocateResource
from networkapi.ip.resource.NetworkIPv6GetResource import NetworkIPv6GetResource
from networkapi.ip.resource.NetworkRemoveResource import NetworkRemoveResource
from networkapi.ip.resource.SearchIPv6EnvironmentResource import SearchIPv6EnvironmentResource

networkip4_get_resource = NetworkIPv4GetResource()
networkip6_get_resource = NetworkIPv6GetResource()
network_edit_resource = NetworkEditResource()
network_add_resource = NetworkAddResource()
network_remove_resource = NetworkRemoveResource()
network_ipv4_add_resource = NetworkIPv4AddResource()
network_ipv4_deallocate_resource = NetworkIPv4DeallocateResource()
network_ipv6_add_resource = NetworkIPv6AddResource()
network_ipv6_deallocate_resource = NetworkIPv6DeallocateResource()
search_ipv6_environment = SearchIPv6EnvironmentResource()

urlpatterns = patterns(
    '',
    url(r'^ipv4/id/(?P<id_rede4>[^/]+)/$', networkip4_get_resource.handle_request,
        name='network.ip4.get.by.id'),
    url(r'^ipv6/id/(?P<id_rede6>[^/]+)/$', networkip6_get_resource.handle_request,
        name='network.ip6.get.by.id'),
    url(r'^add/$', network_add_resource.handle_request,
        name='network.add'),
    url(r'^edit/$', network_edit_resource.handle_request,
        name='network.edit'),
    url(r'^create/$', network_edit_resource.handle_request,
        name='network.create'),
    url(r'^remove/$', network_remove_resource.handle_request,
        name='network.remove'),
    url(r'^ipv4/add/$', network_ipv4_add_resource.handle_request,
        name='network.ipv4.add'),
    url(r'^ipv4/(?P<id_network_ipv4>[^/]+)/deallocate/$', network_ipv4_deallocate_resource.handle_request,
        name='network.ipv4.deallocate'),
    url(r'^ipv6/add/$', network_ipv6_add_resource.handle_request,
        name='network.ipv6.add'),
    url(r'^ipv6/(?P<id_network_ipv6>[^/]+)/deallocate/$', network_ipv6_deallocate_resource.handle_request,
        name='network.ipv6.deallocate')
)
