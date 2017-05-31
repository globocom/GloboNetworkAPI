# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ambiente.resource.GroupL3AddResource import GroupL3AddResource
from networkapi.ambiente.resource.GroupL3AlterRemoveResource import GroupL3AlterRemoveResource
from networkapi.ambiente.resource.GroupL3GetAllResource import GroupL3GetAllResource

group_l3_add_resource = GroupL3AddResource()
group_l3_alter_remove_resource = GroupL3AlterRemoveResource()
group_l3_get_all_resource = GroupL3GetAllResource()

urlpatterns = patterns(
    '',
    url(r'^$', group_l3_add_resource.handle_request,
        name='group_l3.add'),
    url(r'^all/$', group_l3_get_all_resource.handle_request,
        name='group_l3.get.all'),
    url(r'^(?P<id_groupl3>[^/]+)/$', group_l3_alter_remove_resource.handle_request,
        name='group_l3.update.remove.by.pk')
)
