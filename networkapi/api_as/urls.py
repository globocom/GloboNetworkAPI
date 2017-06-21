# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

v3_prefix = r'^v3/'

urlpatterns = patterns(
    '',
    url(v3_prefix, include('networkapi.api_as.v3.urls')),

)
