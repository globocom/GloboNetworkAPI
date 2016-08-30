# -*- coding:utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_environment import views

urlpatterns = patterns(
    '',
    url(r'^v3/environment/(?P<environment_ids>[;\d]+)/$', views.EnvironmentDBView.as_view()),
)
