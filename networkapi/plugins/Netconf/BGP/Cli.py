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


import logging
import os

from django.db.models import Q
from django.template import Context
from django.template import Template

from networkapi.api_deploy import exceptions as deploy_exc
from networkapi.api_equipment.exceptions import \
    AllEquipmentsAreInMaintenanceException
from networkapi.api_neighbor.models import NeighborV4
from networkapi.api_neighbor.models import NeighborV6
from networkapi.equipamento import models as eqpt_models
from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.infrastructure.ipaddr import IPAddress
from networkapi.settings import BGP_CONFIG_FILES_PATH
from networkapi.settings import BGP_CONFIG_TEMPLATE_PATH
from networkapi.settings import BGP_CONFIG_TOAPPLY_REL_PATH
from networkapi.settings import TFTPBOOT_FILES_PATH
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS
from networkapi.plugins.Netconf.plugin import GenericNetconf

log = logging.getLogger(__name__)

class Generic(GenericNetconf):

    TEMPLATE_NEIGHBOR_V4_ADD = 'neighbor_v4_add'
    TEMPLATE_NEIGHBOR_V4_REMOVE = 'neighbor_v4_remove'
    TEMPLATE_NEIGHBOR_V6_ADD = 'neighbor_v6_add'
    TEMPLATE_NEIGHBOR_V6_REMOVE = 'neighbor_v6_remove'
    TEMPLATE_LIST_CONFIG_ADD = 'list_config_add'
    TEMPLATE_LIST_CONFIG_REMOVE = 'list_config_remove'
    TEMPLATE_ROUTE_MAP_ADD = 'route_map_add'
    TEMPLATE_ROUTE_MAP_REMOVE = 'route_map_remove'

    def bgp(self):
        return Generic(equipment=self.equipment)

    def _deploy_pre_req(self, neighbor):
        log.info("_deploy_pre_req")

        # Concatenate RouteMapEntries Lists
        route_map_in = neighbor.peer_group.route_map_in
        route_map_out = neighbor.peer_group.route_map_out

        rms = route_map_in.route_map_entries | \
            route_map_out.route_map_entries

        for rm_entry in rms:
            list_config_bgp = rm_entry.list_config_bgp

            if not list_config_bgp.equipments.filter(id=self.equipment.id):
                self.deploy_list_config_bgp(list_config_bgp)

    @staticmethod
    def _get_type_list(type_):
        types = {
            'P': {
                'config_list': 'prefix-list',
                'route_map': 'ip address prefix-list'
            },
            'C': {
                'config_list': 'community',
                'route_map': ''
            },
        }
        return types[type_]


    def _generate_template_dict_route_map(self, route_map):
        """
        Make a dictionary to use in template
        """

        entries = []

        for entry_obj in route_map.routemapentry_set.all():
            action = 'permit' if entry_obj.action == 'P' else 'deny'
            entry = {
                'ACTION': action,
                'ORDER': entry_obj.order,
                'TYPE_MATCH': self._get_type_list(
                    entry_obj.list_config_bgp.type)['route_map'],
                'LIST': entry_obj.list_config_bgp.name,
                'ACTION_RECONFIG': entry_obj.action_reconfig
            }

            entries.append(entry)

        key_dict = {
            'NAME': route_map.name,
            'ENTRIES': entries
        }

        return key_dict

    def _operate_equipment(self, types, template_type, config):
        # TODO
        return

    def deploy_route_map(self, route_map):
        """
        Deploy route map
        """

        log.info("Deploy route map")

        config = self._generate_template_dict_route_map(route_map)

        self._operate_equipment(
            'route_map', self.TEMPLATE_ROUTE_MAP_ADD, config
        )


