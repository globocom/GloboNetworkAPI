# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ip.resource.IpCheckForVipResource import IpCheckForVipResource
from networkapi.ip.resource.IPEquipEvipResource import IPEquipEvipResource
from networkapi.ip.resource.IPGetByEquipResource import IPGetByEquipResource
from networkapi.ip.resource.IpGetOctBlockResource import IpGetOctBlockResource
from networkapi.ip.resource.IpResource import IpResource
from networkapi.ip.resource.Ipv4GetAvailableForVipResource import Ipv4GetAvailableForVipResource
from networkapi.ip.resource.IPv4GetAvailableResource import IPv4GetAvailableResource
from networkapi.ip.resource.Ipv4GetByIdResource import Ipv4GetByIdResource
from networkapi.ip.resource.IPv4GetResource import IPv4GetResource
from networkapi.ip.resource.IPv4ListResource import IPv4ListResource
from networkapi.ip.resource.Ipv6GetAvailableForVipResource import Ipv6GetAvailableForVipResource
from networkapi.ip.resource.IPv6GetAvailableResource import IPv6GetAvailableResource
from networkapi.ip.resource.Ipv6GetByIdResource import Ipv6GetByIdResource
from networkapi.ip.resource.IPv6ListResource import IPv6ListResource

ip_resource = IpResource()
networkip4_list_ip_resource = IPv4ListResource()
networkip6_list_ip_resource = IPv6ListResource()
ip6_available_vip_resource = Ipv6GetAvailableForVipResource()
ip4_available_vip_resource = Ipv4GetAvailableForVipResource()
ip4_available_resource = IPv4GetAvailableResource()
ip6_available_resource = IPv6GetAvailableResource()

ipv4_get_resource = Ipv4GetByIdResource()
ipv6_get_resource = Ipv6GetByIdResource()
ipv4_get_by_id_resource = IPv4GetResource()
ip_get_by_oct_block = IpGetOctBlockResource()
ip_check_for_vip = IpCheckForVipResource()
ip_equip_evip_resource = IPEquipEvipResource()
ip_get_by_equip_resource = IPGetByEquipResource()

urlpatterns = patterns(
    '',
    url(r'^(?P<id_ip>[^/]+)/equipamento/(?P<id_equipamento>[^/]+)/$',
        ip_resource.handle_request, name='ipequipment.insert.remove'),
    url(r'^(?P<ip>.+)/ambiente/(?P<id_amb>[^/]+)/$',
        ip_resource.handle_request, name='ip.get.by.ip.environment'),
    url(r'^id_network_ipv4/(?P<id_rede>[^/]+)/',
        networkip4_list_ip_resource.handle_request, name='ip4.list.by.network'),
    url(r'^id_network_ipv6/(?P<id_rede>[^/]+)/',
        networkip6_list_ip_resource.handle_request, name='ip6.list.by.network'),
    url(r'^availableip6/vip/(?P<id_evip>[^/]+)/',
        ip6_available_vip_resource.handle_request, name='ip6.get.available.for.vip'),
    url(r'^availableip4/vip/(?P<id_evip>[^/]+)/',
        ip4_available_vip_resource.handle_request, name='ip4.get.available.for.vip'),
    url(r'^availableip4/(?P<id_rede>[^/]+)/',
        ip4_available_resource.handle_request, name='ip4.get.available'),
    url(r'^availableip6/(?P<id_rede>[^/]+)/',
        ip6_available_resource.handle_request, name='ip6.get.available'),
    url(r'^$', ip_resource.handle_request,
        name='ip.insert'),
    url(r'^get-ipv4/(?P<id_ip>[^/]+)/$',
        ipv4_get_resource.handle_request, name='ipv4.get.by.pk'),
    url(r'^get-ipv6/(?P<id_ip>[^/]+)/$',
        ipv6_get_resource.handle_request, name='ipv6.get.by.pk'),
    url(r'^get-ipv4/$',
        ip_resource.handle_request, name='ip.insert'),
    url(r'^get/(?P<id_ip>[^/]+)/',
        ipv4_get_by_id_resource.handle_request, name='ip4.get.by.id'),
    url(r'^getbyoctblock/', ip_get_by_oct_block.handle_request,
        name='ip.get.by.oct.or.block'),
    url(r'^checkvipip/', ip_check_for_vip.handle_request,
        name='ip.check.for.vip'),
    url(r'^getbyequipandevip/$', ip_equip_evip_resource.handle_request,
        name='ip.get.by.equip.and.evip'),
    url(r'^getbyequip/(?P<id_equip>[^/]+)/',
        ip_get_by_equip_resource.handle_request, name='ip.get.by.equip'),

)
