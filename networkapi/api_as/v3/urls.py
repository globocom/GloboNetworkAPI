# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_as.v3 import views

urlpatterns = patterns(
    '',
    url(r'^as/((?P<obj_ids>[;\w]+)/)?$',
        views.AsDBView.as_view()),
)
