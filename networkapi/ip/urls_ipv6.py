# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ip.resource.IPv6AddResource import IPv6AddResource
from networkapi.ip.resource.Ipv6AssocEquipResource import Ipv6AssocEquipResource
from networkapi.ip.resource.Ipv6AssociateResource import Ipv6AssociateResource
from networkapi.ip.resource.IPv6DeleteResource import IPv6DeleteResource
from networkapi.ip.resource.IPv6EditResource import IPv6EditResource
from networkapi.ip.resource.IPv6GetResource import IPv6GetResource
from networkapi.ip.resource.Ipv6RemoveResource import Ipv6RemoveResource
from networkapi.ip.resource.IPv6SaveResource import IPv6SaveResource
from networkapi.ip.resource.SearchIPv6EnvironmentResource import SearchIPv6EnvironmentResource

ipv6_edit_resource = IPv6EditResource()
ipv6_get_by_id_resource = IPv6GetResource()
ipv6_delete_resource = IPv6DeleteResource()
ipv6_save_resource = IPv6SaveResource()
ipv6_add_resource = IPv6AddResource()
ipv6_associate = Ipv6AssociateResource()
ipv6_remove = Ipv6RemoveResource()
search_ipv6_environment = SearchIPv6EnvironmentResource()
ipv6_assoc_equip_resource = Ipv6AssocEquipResource()

urlpatterns = patterns(
    '',
    url(r'^edit',
        ipv6_edit_resource.handle_request, name='ip6.edit'),
    url(r'^get/(?P<id_ipv6>[^/]+)/',
        ipv6_get_by_id_resource.handle_request, name='ip6.get.by.id'),
    url(r'^delete/(?P<id_ipv6>[^/]+)',
        ipv6_delete_resource.handle_request, name='ip6.delete'),
    url(r'^save/$',
        ipv6_save_resource.handle_request, name='ipv6.save'),
    url(r'^$', ipv6_add_resource.handle_request,
        name='ipv6.insert'),
    url(r'^(?P<id_ipv6>[^/]+)/equipment/(?P<id_equip>[^/]+)/$',
        ipv6_associate.handle_request, name='ipv6equipment.associate'),
    url(r'^(?P<id_ipv6>[^/]+)/equipment/(?P<id_equip>[^/]+)/remove/$',
        ipv6_remove.handle_request, name='ipv6equipment.remove'),
    url(r'^environment/$', search_ipv6_environment.handle_request,
        name='ipv6.get.by.ip.environment'),
    url(r'^assoc/$', ipv6_assoc_equip_resource.handle_request,
        name='ipv6.assoc.equip'),

)
