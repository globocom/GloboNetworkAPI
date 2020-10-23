# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_asn.v4 import views

urlpatterns = patterns(
    '',
    url(r'^asnequipment/asn/((?P<asn_ids>[;\w]+)/)?$',
        views.AsEquipmentDBView.as_view()),
    url(r'^asnequipment/equipment/((?P<equip_ids>[;\w]+)/)?$',
        views.AsEquipmentDBView.as_view()),
    url(r'^asnequipment/((?P<obj_ids>[;\w]+)/)?$',
        views.AsEquipmentDBView.as_view()),
    url(r'^as/((?P<obj_ids>[;\w]+)/)?$',
        views.AsDBView.as_view()),
)
