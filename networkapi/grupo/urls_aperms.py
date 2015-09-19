# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from networkapi.grupo.resource.AdministrativePermissionAddResource import AdministrativePermissionAddResource
from networkapi.grupo.resource.AdministrativePermissionAlterRemoveResource import AdministrativePermissionAlterRemoveResource
from networkapi.grupo.resource.AdministrativePermissionByGroupUserResource import AdministrativePermissionByGroupUserResource
from networkapi.grupo.resource.AdministrativePermissionGetAllResource import AdministrativePermissionGetAllResource
from networkapi.grupo.resource.AdministrativePermissionGetByIdResource import AdministrativePermissionGetByIdResource

aperms_get_by_group = AdministrativePermissionByGroupUserResource()
aperms_add_resource = AdministrativePermissionAddResource()
aperms_get_by_pk_resource = AdministrativePermissionGetByIdResource()
aperms_get_all_resource = AdministrativePermissionGetAllResource()
aperms_alter_remove_resource = AdministrativePermissionAlterRemoveResource()

urlpatterns = patterns('',
    url(r'^$', aperms_add_resource.handle_request,
        name='administrative.permission.add'),
    url(r'^all/$', aperms_get_all_resource.handle_request,
        name='administrative.permission.get.all'),
    url(r'^(?P<id_perm>[^/]+)/$', aperms_alter_remove_resource.handle_request,
        name='administrative.permission.update.remove.by.pk'),
    url(r'^group/(?P<id_ugroup>[^/]+)/$', aperms_get_by_group.handle_request,
        name='administrative.permission.get.by.group'),
    url(r'^get/(?P<id_perm>[^/]+)/$', aperms_get_by_pk_resource.handle_request,
        name='administrative.permission.get.by.pk')
)