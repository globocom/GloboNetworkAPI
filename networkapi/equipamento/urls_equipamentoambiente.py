# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.equipamento.resource.EquipamentoResource import EquipamentoAmbienteResource

equipment_environment_resource = EquipamentoAmbienteResource()

urlpatterns = patterns(
    '',
    url(r'^$', equipment_environment_resource.handle_request,
        name='equipmentenvironment.insert'),
    url(r'^update/$', equipment_environment_resource.handle_request,
        name='equipmentenvironment.update')
)
