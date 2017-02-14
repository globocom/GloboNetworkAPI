# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ambiente.resource.AmbienteResource import AmbienteEquipamentoResource
from networkapi.ambiente.resource.AmbienteResource import AmbienteResource
from networkapi.ambiente.resource.EnvironmentGetByEquipResource import EnvironmentGetByEquipResource
from networkapi.ambiente.resource.EnvironmentListResource import EnvironmentListResource

environment_resource = AmbienteResource()
environment_list_resource = EnvironmentListResource()
environment_by_equip_resource = EnvironmentGetByEquipResource()
environment_equip_resource = AmbienteEquipamentoResource()

urlpatterns = patterns(
    '',
    url(r'^$', environment_resource.handle_request,
        name='environment.search.insert'),
    url(r'^list/$', environment_list_resource.handle_request,
        name='environment.list.all'),
    url(r'^equip/(?P<id_equip>[^/]+)/$', environment_by_equip_resource.handle_request,
        name='environment.list.by.equip'),
    # url(r'^ipconfig/$', environment_resource.handle_request, {'ip_config': True},
    #     name='environment.insert.ipconfig'),
    url(r'^divisao_dc/(?P<id_divisao_dc>[^/]+)/$', environment_resource.handle_request,
        name='environment.search.by.divisao_dc'),
    url(r'^divisao_dc/(?P<id_divisao_dc>[^/]+)/ambiente_logico/(?P<id_amb_logico>[^/]+)/$', environment_resource.handle_request,
        name='environment.search.by.divisao_dc.logic_environment'),
    # url(r'^equipamento/(?P<nome_equip>[^/]+)/ip/(?P<x1>\d{1,3})\.(?P<x2>\d{1,3})\.(?P<x3>\d{1,3})\.(?P<x4>\d{1,3})/$',environment_equip_resource.handle_request,
    #     name='environment.get.by.equipment_name.ip'),
    url(r'^(?P<id_ambiente>[^/]+)/$', environment_resource.handle_request,
        name='environment.search.update.remove.by.pk')
)
