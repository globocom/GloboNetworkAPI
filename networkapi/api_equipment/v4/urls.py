# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_equipment.v4.views import EquipmentPortChannelV4View
from networkapi.api_equipment.v4.views import EquipmentV4View


urlpatterns = patterns(
    '',
    url(r'^equipment/((?P<obj_id>[;\w]+)/)?$', EquipmentV4View.as_view()),
    url(r'^equipment/(?P<obj_id>\d+)/port-channel/'
        r'(?P<channel_name>(?:ae)?\d+)/?$',
        EquipmentPortChannelV4View.as_view()),

)
