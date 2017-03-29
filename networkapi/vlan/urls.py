# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ambiente.models import IP_VERSION
from networkapi.vlan.resource.VlanAllocateIPv6Resorce import VlanAllocateIPv6Resorce
from networkapi.vlan.resource.VlanAllocateResource import VlanAllocateResource
from networkapi.vlan.resource.VlanApplyAcl import VlanApplyAcl
from networkapi.vlan.resource.VlanCheckNumberAvailable import VlanCheckNumberAvailable
from networkapi.vlan.resource.VlanCreateAclResource import VlanCreateAclResource
from networkapi.vlan.resource.VlanCreateResource import VlanCreateResource
from networkapi.vlan.resource.VlanCreateScriptAclResource import VlanCreateScriptAclResource
from networkapi.vlan.resource.VlanDeallocateResource import VlanDeallocateResource
from networkapi.vlan.resource.VlanEditResource import VlanEditResource
from networkapi.vlan.resource.VlanFindResource import VlanFindResource
from networkapi.vlan.resource.VlanGetByEnvironmentResource import VlanGetByEnvironmentResource
from networkapi.vlan.resource.VlanInsertResource import VlanInsertResource
from networkapi.vlan.resource.VlanInvalidateResource import VlanInvalidateResource
from networkapi.vlan.resource.VlanListResource import VlanListResource
from networkapi.vlan.resource.VlanRemoveResource import VlanRemoveResource
from networkapi.vlan.resource.VlanResource import VlanResource
from networkapi.vlan.resource.VlanSearchResource import VlanSearchResource
from networkapi.vlan.resource.VlanValidateResource import VlanValidateResource

vlan_resource = VlanResource()
vlan_list_resource = VlanListResource()
vlan_search_resource = VlanSearchResource()
vlan_find_resource = VlanFindResource()
vlan_allocate_resource = VlanAllocateResource()
vlan_remove_resource = VlanRemoveResource()
vlan_deallocate_resource = VlanDeallocateResource()
vlan_allocate_ipv6_resource = VlanAllocateIPv6Resorce()
vlan_create_resource = VlanCreateResource()
vlan_insert_resource = VlanInsertResource()
vlan_edit_resource = VlanEditResource()
vlan_invalidate_resource = VlanInvalidateResource()
vlan_validate_resource = VlanValidateResource()
vlan_check_number_available_resource = VlanCheckNumberAvailable()
vlan_get_by_env_resource = VlanGetByEnvironmentResource()
vlan_apply_resource = VlanApplyAcl()
vlan_create_acl_resource = VlanCreateAclResource()
vlan_create_script_acl_resource = VlanCreateScriptAclResource()


urlpatterns = patterns(
    '',
    url(r'^$', vlan_resource.handle_request,
        name='vlan.allocate'),
    url(r'^all/$', vlan_list_resource.handle_request,
        name='vlan.list.all'),
    url(r'^find/$',
        vlan_find_resource.handle_request, name='vlan.find'),
    url(r'^ipv6/$', vlan_allocate_ipv6_resource.handle_request,
        name='vlan.allocate.ipv6'),
    url(r'^no-network/$', vlan_allocate_resource.handle_request,
        name='vlan.allocate.without.network'),
    url(r'^(?P<operacao>list)/$',
        vlan_resource.handle_request, name='vlan.list'),
    url(r'^insert/$', vlan_insert_resource.handle_request,
        name='vlan.insert'),
    url(r'^edit/$',
        vlan_edit_resource.handle_request, name='vlan.edit'),
    url(r'^create/$', vlan_edit_resource.handle_request,
        name='vlan.create'),
    url(r'^(?P<id_vlan>[^/]+)/$',
        vlan_resource.handle_request, name='vlan.get.by.pk'),
    url(r'^(?P<id_vlan>[^/]+)/remove/$',
        vlan_remove_resource.handle_request, name='vlan.remove.by.pk'),
    url(r'^(?P<id_vlan>[^/]+)/network/$',
        vlan_search_resource.handle_request, name='vlan.network.get.by.pk'),
    url(r'^(?P<id_vlan>[^/]+)/deallocate/$',
        vlan_deallocate_resource.handle_request, name='vlan.deallocate'),
    url(r'^ambiente/(?P<id_ambiente>[^/]+)/$',
        vlan_get_by_env_resource.handle_request, name='vlan.search.by.environment'),
    url(r'^(?P<id_vlan>[^/]+)/invalidate/(?P<network>v4|v6)/$',
        vlan_invalidate_resource.handle_request, name='vlan.invalidate'),
    url(r'^(?P<id_vlan>[^/]+)/validate/(?P<network>v4|v6)/$',
        vlan_validate_resource.handle_request, name='vlan.validate'),
    url(r'^(?P<id_vlan>[^/]+)/(?P<operacao>criar|add|del|check)/$',
        vlan_resource.handle_request, name='vlan.create.add.remove.check.validate'),
    url(r'^v4/create/$', vlan_create_resource.handle_request,
        {'network_version': IP_VERSION.IPv4[0]}, name='vlan.create.v4'),
    url(r'^v6/create/$', vlan_create_resource.handle_request,
        {'network_version': IP_VERSION.IPv6[0]}, name='vlan.create.v6'),
    url(r'^confirm/(?P<number>[^/]+)/(?P<id_environment>[^/]+)/(?P<ip_version>[^/]+)/$',
        vlan_validate_resource.handle_request, name='vlan.confirm.vlan'),
    url(r'^check_number_available/(?P<id_environment>[^/]+)/(?P<num_vlan>[^/]+)/(?P<id_vlan>[^/]+)/$',
        vlan_check_number_available_resource.handle_request, name='vlan.check.num.available'),
    url(r'^apply/acl/$', vlan_apply_resource.handle_request,
        name='vlan.apply.acl'),

    url(r'^create/acl/$', vlan_create_acl_resource.handle_request,
        name='vlan.create.acl'),
    url(r'^create/script/acl/$',
        vlan_create_script_acl_resource.handle_request, name='vlan.create.script.acl'),
)
