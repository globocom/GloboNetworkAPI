# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.equipamento.resource.EquipamentoGrupoResource import EquipamentoGrupoResource
from networkapi.grupo.resource.GrupoEquipamentoAssociaEquipamentoResource import GrupoEquipamentoAssociaEquipamentoResource

equipment_group_resource = EquipamentoGrupoResource()
equipment_group_associa_resource = GrupoEquipamentoAssociaEquipamentoResource()

urlpatterns = patterns(
    '',
    url(r'^$', equipment_group_resource.handle_request,
        name='equipmentgroup.insert'),
    url(r'^associa/$', equipment_group_associa_resource.handle_request,
        name='equipmentgroup.associa'),
    url(r'^equipamento/(?P<id_equip>[^/]+)/egrupo/(?P<id_egrupo>[^/]+)/$', equipment_group_resource.handle_request,
        name='equipmentgroup.remove')
)
