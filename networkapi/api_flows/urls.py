# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_flows import views

urlpatterns = patterns(
    '',
    url(r'^v3/apply/flow/$', views.FlowsView.as_view()),
)
