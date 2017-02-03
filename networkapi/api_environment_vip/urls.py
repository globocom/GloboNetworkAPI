# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_environment_vip import views

urlpatterns = patterns(
    '',
    url(r'^v3/environment-vip/step/$', views.EnvironmentVipStepOneView.as_view()),
    url(r'^v3/environment-vip/((?P<obj_id>[;\w]+)/)?$',
        views.EnvironmentVipView.as_view()),
    url(r'^v3/option-vip/environment-vip/(?P<environment_vip_id>\d+)/$',
        views.OptionVipEnvironmentVipOneView.as_view()),
    url(r'^v3/option-vip/environment-vip/(?P<environment_vip_id>[;\w]+)'
        '/type-option/(?P<type_option>[\w|\W]+)/$',
        views.OptionVipEnvironmentTypeVipView.as_view()),
    url(r'^v3/type-option/environment-vip/(?P<environment_vip_id>[;\w]+)/$',
        views.TypeOptionEnvironmentVipView.as_view()),
)
