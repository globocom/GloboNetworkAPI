# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_peer_group.v4 import views

urlpatterns = patterns(
    '',
    url(r'^peer-group/(?P<peer_group_id>\d+)/environment/?$',
        views.EnvironmentPeerGroupDBView.as_view()),
    url(r'^peer-group/(?P<peer_group_id>\d+)/environment/(?P<environment_id>\d+)/?$',
        views.EnvironmentPeerGroupDBView.as_view()),
    url(r'^peer-group/((?P<obj_ids>[;\w]+)/)?$',
        views.PeerGroupDBView.as_view()),
)
