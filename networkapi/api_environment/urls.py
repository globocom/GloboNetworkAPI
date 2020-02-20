# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_environment import views

urlpatterns = patterns(
    '',
    url(r'^v3/cidr/environment/((?P<env_id>[;\w]+)/)?$',
        views.EnvironmentCIDRDBView.as_view()),
    url(r'^v3/cidr/((?P<cidr_id>[;\w]+)/)?$',
        views.EnvironmentCIDRDBView.as_view()),
    url(r'^v3/environment/dc/((?P<obj_ids>[;\w]+)/)?$',
        views.EnvironmentDCDBView.as_view()),
    url(r'^v3/environment/l3/((?P<obj_ids>[;\w]+)/)?$',
        views.EnvironmentL3DBView.as_view()),
    url(r'^v3/environment/logic/((?P<obj_ids>[;\w]+)/)?$',
        views.EnvironmentLogicDBView.as_view()),
    url(r'^v3/environment/((?P<obj_ids>[;\w]+)/)?$',
        views.EnvironmentDBView.as_view()),
    url(r'^v3/environment/environment-vip/((?P<environment_vip_id>\d+)/)?$',
        views.EnvEnvVipRelatedView.as_view()),
    url(r'^v3/environment/((?P<environment_id>\d+)/)?flows/((?P<flow_id>\d+)/)?$',
        views.EnvFlowView.as_view()),
)
