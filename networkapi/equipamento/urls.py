# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.equipamento.resource.EquipamentoEditResource import EquipamentoEditResource
from networkapi.equipamento.resource.EquipamentoResource import EquipamentoResource
from networkapi.equipamento.resource.EquipmentFindResource import EquipmentFindResource
from networkapi.equipamento.resource.EquipmentGetRealRelated import EquipmentGetRealRelated
from networkapi.equipamento.resource.EquipmentListResource import EquipmentListResource

equipment_resource = EquipamentoResource()
equipment_get_real_related = EquipmentGetRealRelated()
equipment_edit_resource = EquipamentoEditResource()
equipment_list_resource = EquipmentListResource()
equipment_find_resource = EquipmentFindResource()

urlpatterns = patterns(
    '',
    url(r'^get_real_related/(?P<id_equip>[^/]+)/$',
        equipment_get_real_related.handle_request, name='equipment.get.real.related'),
    url(r'^$', equipment_resource.handle_request,
        name='equipment.insert'),
    url(r'^edit/(?P<id_equip>[^/]+)/$',
        equipment_edit_resource.handle_request, name='equipment.edit.by.pk'),
    url(r'^list/$', equipment_list_resource.handle_request,
        name='equipment.list.all'),
    url(r'^find/$',
        equipment_find_resource.handle_request, name='equipment.find'),
    url(r'^(?P<id_equip>[^/]+)/$',
        equipment_resource.handle_request, name='equipment.remove.by.pk'),
    url(r'^nome/(?P<nome_equip>[^/]+)/$',
        equipment_resource.handle_request, name='equipment.get.by.name'),
    url(r'^id/(?P<id_equip>[^/]+)/$',
        equipment_resource.handle_request, name='equipment.get.by.id'),
    url(r'^tipoequipamento/(?P<id_tipo_equip>[^/]+)/ambiente/(?P<id_ambiente>[^/]+)/$',
        equipment_resource.handle_request, name='equipment.search.by.equipment_type.environment'),
)
