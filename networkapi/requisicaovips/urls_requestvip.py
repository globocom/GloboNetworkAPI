# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.requisicaovips.resource.RequestVipGetByIdResource import RequestVipGetByIdResource
from networkapi.requisicaovips.resource.RequestVipGetIdIpResource import RequestVipGetIdIpResource
from networkapi.requisicaovips.resource.RequestVipsResource import RequestVipsResource

vip_request = RequestVipsResource()
vip_request_get_id = RequestVipGetByIdResource()
vip_request_get_ip_id = RequestVipGetIdIpResource()

urlpatterns = patterns(
    '',
    url(r'^$', vip_request.handle_request,
        name='requestvip.insert'),
    url(r'^get_by_ip_id/$', vip_request_get_ip_id.handle_request,
        name='requestvip.get.by.id.ip'),
    url(r'^getbyid/(?P<id_vip>[^/]+)/$', vip_request_get_id.handle_request,
        name='requestvip.get.by.pk'),
    # url(r'^(?P<id_vip>[^/]+)/$', vip_request.handle_request,
    #     name='requestvip.update.by.pk')
)
