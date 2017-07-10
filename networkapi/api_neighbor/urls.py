# -*- coding: utf-8 -*-
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns(
    '',
    url('v3/', include('networkapi.api_neighbor.v3.urls')),

)
