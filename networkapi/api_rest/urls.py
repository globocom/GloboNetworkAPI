# -*- coding:utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_rest import views

urlpatterns = patterns(
    'networkapi.api_rest.views',
    url(r'^v3/help/(?P<way>[_\w]+)/$', views.HelperApi.as_view()),  # GET
)
