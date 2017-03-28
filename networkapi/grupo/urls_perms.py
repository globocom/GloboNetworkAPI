# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.grupo.resource.PermissionGetAllResource import PermissionGetAllResource

perms_get_all_resource = PermissionGetAllResource()

urlpatterns = patterns(
    '',
    url(r'^all/$', perms_get_all_resource.handle_request,
        name='permission.get.all')
)
