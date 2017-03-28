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

from networkapi.api_interface.views import DisconnectView

urlpatterns = patterns('networkapi.api_interface.views',
                       url(r'^interface/(?P<id_interface>\d+)/deploy_config_sync/$',
                           'deploy_interface_configuration_sync'),
                       url(r'^interface/channel/(?P<id_channel>\d+)/deploy_config_sync/$',
                           'deploy_channel_configuration_sync'),
                       url(r'^interface/disconnect/(?P<id_interface_1>\d+)/(?P<id_interface_2>\d+)/$',
                           DisconnectView.as_view()),
                       )
