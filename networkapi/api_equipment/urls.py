# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from networkapi.api_equipment.views import EquipmentView


urlpatterns = patterns('',
    url(r'^equipment/get_routers_by_environment/(?P<env_id>\d+)/$', EquipmentView.as_view()),
)