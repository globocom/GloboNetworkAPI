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

from networkapi.api_interface.views import DeployInterfaceConfV3View
from networkapi.api_interface.views import DisconnectView
from networkapi.api_interface.views import InterfaceEnvironmentsV3View
from networkapi.api_interface.views import InterfaceTypeV3View
from networkapi.api_interface.views import InterfaceV3ConnectionsView
from networkapi.api_interface.views import InterfaceV3View


urlpatterns = patterns(
    'networkapi.api_interface.views',

    url(r'^interface/disconnect/(?P<id_interface_1>\d+)/(?P<id_interface_2>\d+)/$',
        DisconnectView.as_view()),
    url(r'^interface/(?P<interface_id>\d+)/deploy_config_sync/$',
        DeployInterfaceConfV3View.as_view()),

    url(r'^v3/connections/(?P<interface_a>[;\w]+)/((?P<interface_b>[;\w]+)[/])$',
        InterfaceV3ConnectionsView.as_view()),
    url(r'^v3/interface/environments/((?P<obj_ids>[;\w]+)[/])?$',
        InterfaceEnvironmentsV3View.as_view()),
    url(r'^v3/interface/environments[/]?$',
        InterfaceEnvironmentsV3View.as_view()),
    url(r'^v3/interface/((?P<obj_ids>[;\w]+)[/])?$',
       InterfaceV3View.as_view()),

    url(r'^v3/interfacetype/((?P<obj_ids>[;\w]+)[/])?$',
       InterfaceTypeV3View.as_view()),
)
