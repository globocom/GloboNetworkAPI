# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_pools.views import v3 as views_v3

urlpatterns = patterns(
    'networkapi.api_pools.views.v1',
    # url(r'^pools/save/$', 'save'),
    # url(r'^pools/save_reals/$', 'save_reals'),
    # url(r'^pools/delete/$', 'delete'),
    # url(r'^pools/remove/$', 'remove'),
    # url(r'^pools/create/$', 'create'),
    # url(r'^pools/enable/$', 'enable'),
    # url(r'^pools/disable/$', 'disable'),

    url(r'^pools/$', 'pool_list'),
    url(r'^pools/pool_list_by_reqvip/$', 'pool_list_by_reqvip'),
    # url(r'^pools/list_healthchecks/$', 'healthcheck_list'),
    url(r'^pools/getbypk/(?P<id_server_pool>[^/]+)/$', 'get_by_pk'),
    url(r'^pools/get_all_members/(?P<id_server_pool>[^/]+)/$',
        'list_all_members_by_pool'),
    # url(r'^pools/get_equip_by_ip/(?P<id_ip>[^/]+)/$', 'get_equipamento_by_ip'),
    # url(r'^pools/get_opcoes_pool_by_ambiente/$', 'get_opcoes_pool_by_ambiente'),
    # url(
    #     r'^pools/get_requisicoes_vip_by_pool/(?P<id_server_pool>[^/]+)/$', 'get_requisicoes_vip_by_pool'),
    # url(
    #     r'^pools/list/by/environment/(?P<environment_id>[^/]+)/$', 'list_by_environment'),
    # url(r'^pools/list/members/(?P<pool_id>[^/]+)/$', 'list_pool_members'),
    url(r'^pools/list/by/environment/vip/(?P<environment_vip_id>\d+)/$',
        'list_by_environment_vip'),
    url(r'^pools/list/environment/with/pools/$', 'list_environments_with_pools'),

    # url(r'^pools/check/status/by/pool/(?P<pool_id>[^/]+)/$',
    #     'chk_status_poolmembers_by_pool'),
    # url(r'^pools/check/status/by/vip/(?P<vip_id>[^/]+)/$',
    #     'chk_status_poolmembers_by_vip'),

    # url(r'^pools/management/$', 'management_pools'),

    url(r'^pools/options/$', 'list_all_options'),
    # url(r'^pools/options/save/$', 'save_pool_option'),
    url(r'^pools/options/(?P<option_id>\d+)/$', 'list_option_by_pk'),

    # url(r'^pools/environment_options/$', 'list_all_environment_options'),
    # url(r'^pools/environment_options/save/$', 'save_environment_options'),
    # url(r'^pools/environment_options/(?P<environment_option_id>\d+)/$',
    #     'environment_options_by_pk'),

    url(r'^pools/list/environments/environmentvip/$',
        'list_environment_environment_vip_related'),
    # url(r'^pools/getipsbyambiente/(?P<equip_name>[^/]+)/(?P<id_ambiente>[^/]+)/$',
    #     'get_available_ips_to_add_server_pool'),


    ########################
    # Manage Pool V3
    ########################
    url(r'^v3/pool/deploy/async/(?P<obj_ids>[;\w]+)/$',
        views_v3.PoolAsyncDeployView.as_view()),
    url(r'^v3/pool/deploy/(?P<obj_ids>[;\w]+)/member/status/$',
        views_v3.PoolMemberStateView.as_view()),
    url(r'^v3/pool/deploy/(?P<obj_ids>[;\w]+)/$',
        views_v3.PoolDeployView.as_view()),
    url(r'^v3/pool/details/((?P<obj_ids>[;\w]+)/)?$',
        views_v3.PoolDBDetailsView.as_view()),
    url(r'^v3/pool/((?P<obj_ids>[;\w]+)/)?$', views_v3.PoolDBView.as_view()),
    url(r'^v3/pool/environment-vip/(?P<environment_vip_id>[^/]+)/$',
        views_v3.PoolEnvironmentVip.as_view()),

    url(r'^v3/option-pool/environment/(?P<environment_id>\d+)/$',
        views_v3.OptionPoolEnvironmentView.as_view()),

    # url(r'^v3/option-pool/((?P<obj_ids>[;\w]+)/)?$',
    #     views_v3.OptionPoolView.as_view()),
)
