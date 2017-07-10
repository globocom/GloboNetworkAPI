# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_neighbor.v3 import views

urlpatterns = patterns(
    url(r'^/((?P<obj_ids>[;\w]+)/)?$', views.NeighborView.as_view()),
)
