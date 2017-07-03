# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.grupo.resource.GroupEquipmentResource import GroupEquipmentResource

egroup_get_resource = GroupEquipmentResource()

urlpatterns = patterns(
    '',
    url(r'^(?P<id_egroup>[^/]+)/$', egroup_get_resource.handle_request,
        name='egroup.get.by.pk')
)
