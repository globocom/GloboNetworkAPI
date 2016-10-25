# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_vrf import views

urlpatterns = patterns(
    'networkapi.api_vrf.views',
    url(r'^v3/vrf/((?P<vrf_ids>[;\w]+)/)?$',
        views.VrfDBView.as_view()),

)
