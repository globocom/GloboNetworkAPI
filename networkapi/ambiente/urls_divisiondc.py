# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ambiente.resource.DivisionDcAddResource import DivisionDcAddResource
from networkapi.ambiente.resource.DivisionDcAlterRemoveResource import DivisionDcAlterRemoveResource
from networkapi.ambiente.resource.DivisionDcGetAllResource import DivisionDcGetAllResource

division_dc_add_resource = DivisionDcAddResource()
division_dc_alter_remove_resource = DivisionDcAlterRemoveResource()
division_dc_get_all_resource = DivisionDcGetAllResource()

urlpatterns = patterns(
    '',
    url(r'^$', division_dc_add_resource.handle_request,
        name='division_dc.add'),
    url(r'^all/$', division_dc_get_all_resource.handle_request,
        name='division_dc.get.all'),
    url(r'^(?P<id_divisiondc>[^/]+)/$', division_dc_alter_remove_resource.handle_request,
        name='division_dc.update.remove.by.pk')
)
