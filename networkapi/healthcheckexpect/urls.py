# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.healthcheckexpect.resource.HealthcheckAddExpectStringResource import HealthcheckAddExpectStringResource
from networkapi.healthcheckexpect.resource.HealthcheckAddResource import HealthcheckAddResource
from networkapi.healthcheckexpect.resource.HealthcheckExpectDistinctResource import HealthcheckExpectDistinctResource
from networkapi.healthcheckexpect.resource.HealthcheckExpectGetResource import HealthcheckExpectGetResource
from networkapi.healthcheckexpect.resource.HealthcheckExpectResource import HealthcheckExpectResource

healthcheckexpect_resource = HealthcheckExpectResource()
healthcheckexpect_add_resource = HealthcheckAddResource()
healthcheckexpect_string_resource = HealthcheckAddExpectStringResource()
healthcheckexpect_distinct_resource = HealthcheckExpectDistinctResource()
healthcheckexpect_get_resource = HealthcheckExpectGetResource()

urlpatterns = patterns(
    '',
    url(r'^ambiente/(?P<id_amb>[^/]+)/$', healthcheckexpect_resource.handle_request,
        name='healthcheckexpect.search.by.environment'),
    url(r'^add/$', healthcheckexpect_add_resource.handle_request,
        name='healthcheckexpect.add'),
    url(r'^add/expect_string/$', healthcheckexpect_string_resource.handle_request,
        name='healthcheckexpect.string.add'),
    url(r'^distinct/busca/$', healthcheckexpect_distinct_resource.handle_request,
        name='healthcheckexpect.distinct'),
    url(r'^get/(?P<id_healthcheck>[^/]+)/$', healthcheckexpect_get_resource.handle_request,
        name='healthcheckexpect.get.by.pk')
)
