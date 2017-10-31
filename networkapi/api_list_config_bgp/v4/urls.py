# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_list_config_bgp.v4 import views

urlpatterns = patterns(
    '',
    url(r'^list-config-bgp/((?P<obj_ids>[;\w]+)/)?$',
        views.ListConfigBGPDBView.as_view()),
)
