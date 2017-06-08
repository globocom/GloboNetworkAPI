# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ambiente.resource.EnvironmentIpConfigResource import EnvironmentIpConfigResource

env_ip_conf_resource = EnvironmentIpConfigResource()

urlpatterns = patterns(
    '',
    url(r'^$', env_ip_conf_resource.handle_request,
        name='ipconfig.associate'),
)
