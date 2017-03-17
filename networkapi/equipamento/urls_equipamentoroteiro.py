# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.equipamento.resource.EquipScriptListResource import EquipScriptListResource

equipment_script_list_resource = EquipScriptListResource()

urlpatterns = patterns(
    '',
    url(r'^name/$', equipment_script_list_resource.handle_request,
        name='equipmentscript.list.by.name'),
)
