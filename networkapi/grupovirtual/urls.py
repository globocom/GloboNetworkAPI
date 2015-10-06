# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from networkapi.grupovirtual.resource.GrupoVirtualResource import GroupVirtualResource

virtual_group_resource = GroupVirtualResource()

urlpatterns = patterns('',
    url(r'^$', virtual_group_resource.handle_request,
       name='virtual_group.add.remove'),
)