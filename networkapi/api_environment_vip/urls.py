# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url

from networkapi.api_environment_vip import views

urlpatterns = patterns(
    '',
    url(r'^environment-vip/step/$', views.EnvironmentVipStepOneView.as_view()),
    url(r'^option-vip/environment-vip/(?P<environment_vip_id>\d+)/$', views.OptionVipEnvironmentVipOneView.as_view()),
    url(r'^option-vip/environment-vip/(?P<environment_vip_id>\d+)/(?P<type_option>\w+)/$', views.OptionVipEnvironmentTypeVipOneView.as_view()),
)