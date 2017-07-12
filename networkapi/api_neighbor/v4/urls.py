# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_neighbor.v4 import views

urlpatterns = patterns(
    '',
    url(r'^neighbor/((?P<obj_ids>[;\w]+)/)?$',
        views.NeighborDBView.as_view()),
)
