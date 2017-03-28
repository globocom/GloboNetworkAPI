# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.requisicaovips.resource.RequestVipsRealResource import RequestVipsRealResource

vip_real = RequestVipsRealResource()

urlpatterns = patterns(
    '',
    url(r'^equip/(?P<id_equip>\d+)/vip/(?P<id_vip>\d+)/ip/(?P<id_ip>\d+)/$', vip_real.handle_request,
        name='vip.real.add.remove'),
    url(r'^(?P<status>enable|disable|check)/equip/(?P<id_equip>\d+)/vip/(?P<id_vip>\d+)/ip/(?P<id_ip>\d+)/$', vip_real.handle_request,
        name='vip.real.enable.disable')
)
