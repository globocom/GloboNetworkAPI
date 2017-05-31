# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_vlan.views import v3 as views


urlpatterns = patterns(
    'networkapi.api_vlan.views.v1',
    url(r'^vlan/acl/remove/draft/(?P<id_vlan>[^/]+)/(?P<acl_type>[^/]+)/$',
        'acl_remove_draft'),
    url(r'^vlan/acl/save/draft/(?P<id_vlan>[^/]+)/(?P<acl_type>[^/]+)/$',
        'acl_save_draft'),


    ########################
    # Vlan V3
    ########################
    url(r'^v3/vlan/async/((?P<obj_ids>[;\w]+)/)?$',
        views.VlanAsyncView.as_view()),
    url(r'^v3/vlan/((?P<obj_ids>[;\w]+)/)?$', views.VlanDBView.as_view()),
)
