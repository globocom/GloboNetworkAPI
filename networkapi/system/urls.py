# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.system.views import VariablebyPkView
from networkapi.system.views import VariableView

urlpatterns = patterns('networkapi.system.views',
                       url(r'^system/variables/$', VariableView.as_view()),
                       url(
                           r'^system/variables/(?P<variable_id>[^/]+)/$', VariablebyPkView.as_view()),
                       )
