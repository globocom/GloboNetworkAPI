# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_ogp import views

urlpatterns = patterns(
    'networkapi.api_ogp.views',
    url(r'^v3/object-group-perm/((?P<ogp_ids>[;\w]+)/)?$',
        views.ObjectGroupPermView.as_view()),
    url(r'^v3/object-group-perm-general/((?P<ogpg_ids>[;\w]+)/)?$',
        views.ObjectGroupPermGeneralView.as_view()),
    url(r'^v3/object-type/((?P<ot_ids>[;\w]+)/)?$',
        views.ObjectTypeView.as_view()),
)
