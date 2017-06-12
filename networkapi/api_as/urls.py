# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_as import views

urlpatterns = patterns(
    '',
    url(r'^v3/as/((?P<obj_ids>[;\w]+)/)?$',
        views.AsDBView.as_view()),
)
