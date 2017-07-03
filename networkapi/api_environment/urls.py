# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_environment import views

urlpatterns = patterns(
    '',
    url(r'^v3/environment/((?P<obj_ids>[;\w]+)/)?$',
        views.EnvironmentDBView.as_view()),
    url(r'^v3/environment/environment-vip/((?P<environment_vip_id>\d+)/)?$',
        views.EnvEnvVipRelatedView.as_view()),
    # url(r'^v3/environment/((?P<environment_id>\d+)/)?flows/$',
    #     views.EnvFlowView.as_view()),
    url(r'^v3/environment/((?P<environment_id>\d+)/)?flows/((?P<flow_id>\d+)/)?$',
        views.EnvFlowView.as_view()),
)
