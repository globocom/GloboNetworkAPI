# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.equipamento.resource.EquipmentScriptAddResource import EquipmentScriptAddResource
from networkapi.equipamento.resource.EquipmentScriptGetAllResource import EquipmentScriptGetAllResource
from networkapi.equipamento.resource.EquipmentScriptRemoveResource import EquipmentScriptRemoveResource

equipment_script_add_resource = EquipmentScriptAddResource()
equipment_script_remove_resource = EquipmentScriptRemoveResource()
equipment_script_get_all_resource = EquipmentScriptGetAllResource()

urlpatterns = patterns(
    '',
    url(r'^$', equipment_script_add_resource.handle_request,
        name='equipment_script.add'),
    url(r'^all/$', equipment_script_get_all_resource.handle_request,
        name='equipment_script.get.all'),
    url(r'^(?P<id_equipment>[^/]+)/(?P<id_script>[^/]+)/$', equipment_script_remove_resource.handle_request,
        name='equipment_script.remove')
)
