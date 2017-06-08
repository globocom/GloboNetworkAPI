# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.grupo.resource.GroupUserAddResource import GroupUserAddResource
from networkapi.grupo.resource.GroupUserAlterRemoveResource import GroupUserAlterRemoveResource
from networkapi.grupo.resource.GroupUserGetAllResource import GroupUserGetAllResource
from networkapi.grupo.resource.GroupUserGetByIdResource import GroupUserGetByIdResource

ugroup_get_all_resource = GroupUserGetAllResource()
ugroup_get_by_id_resource = GroupUserGetByIdResource()
ugroup_alter_remove_resource = GroupUserAlterRemoveResource()
ugroup_add_resource = GroupUserAddResource()

urlpatterns = patterns(
    '',
    url(r'^all/$', ugroup_get_all_resource.handle_request,
        name='ugroup.get.all'),
    url(r'^get/(?P<id_ugroup>[^/]+)/$', ugroup_get_by_id_resource.handle_request,
        name='ugroup.get'),
    url(r'^$', ugroup_add_resource.handle_request,
        name='ugroup.add'),
    url(r'^(?P<id_ugroup>[^/]+)/$', ugroup_alter_remove_resource.handle_request,
        name='ugroup.alter.remove')
)
