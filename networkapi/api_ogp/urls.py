# -*- coding:utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_ogp import views


urlpatterns = patterns(
    ########################
    # Object Perms V3
    ########################

    url(r'^v3/object-group-perm-general/$', views.ObjectGroupPermView.as_view()),

)
