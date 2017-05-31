# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_equipment.views import v1
from networkapi.api_equipment.views import v3


urlpatterns = patterns(
    '',
    url(r'^equipment/get_routers_by_environment/(?P<env_id>\d+)/$',
        v1.EquipmentRoutersView.as_view()),
    url(r'^v3/equipment/((?P<obj_id>[;\w]+)/)?$', v3.EquipmentView.as_view()),
)
