# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_vip_request.views import v3 as views


urlpatterns = patterns(
    'networkapi.api_vip_request.views.v1',
    # url(r'^vip/request/save/?(?P<pk>\d+)?/?$', 'save'),
    # url(r'^vip/request/add/pools/$', 'add_pools'),
    # url(r'^vip/request/delete/(?P<delete_pools>\d+)/$', 'delete'),
    url(r'^vip/list/environment/by/environment/vip/(?P<environment_vip_id>\d+)/$',
        'list_environment_by_environment_vip'),
    url(r'^vip/request/get/(?P<pk>\d+)/$', 'get_by_pk'),


    ########################
    # Vip Resquest V3
    ########################

    url(r'^v3/vip-request/details/((?P<obj_ids>[;\w]+)/)?$',
        views.VipRequestDBDetailsView.as_view()),
    url(r'^v3/vip-request/deploy/async/((?P<obj_ids>[;\w]+)/)?$',
        views.VipRequestAsyncDeployView.as_view()),
    url(r'^v3/vip-request/deploy/((?P<obj_ids>[;\w]+)/)?$',
        views.VipRequestDeployView.as_view()),
    url(r'^v3/vip-request/((?P<obj_ids>[;\w]+)/)?$',
        views.VipRequestDBView.as_view()),
    url(r'^v3/vip-request/pool/(?P<pool_id>[^/]+)/$',
        views.VipRequestPoolView.as_view()),  # GET
)
