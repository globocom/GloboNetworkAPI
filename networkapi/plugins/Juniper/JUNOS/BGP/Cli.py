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

log = logging.getLogger(__name__)


class Generic(JUNOS):

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

        if not route_map_in.equipments.filter(id=self.equipment.id):
            self.deploy_route_map(neighbor.peer_group.route_map_in)

        if not route_map_out.equipments.filter(id=self.equipment.id):
            self.deploy_route_map(neighbor.peer_group.route_map_out)

    def _undeploy_pre_req(self, neighbor, ip_version):

        # Concatenate RouteMapEntries Lists
        route_map_in = neighbor.peer_group.route_map_in
        route_map_out = neighbor.peer_group.route_map_out

        neighbors_v4 = NeighborV4.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_in) |
            Q(peer_group__route_map_out=route_map_in))
        ).filter(created=True)

        neighbors_v6 = NeighborV6.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_in) |
            Q(peer_group__route_map_out=route_map_in))
        ).filter(created=True)

        if ip_version == 6:
            neighbors_v6.filter(
                ~Q(id=neighbor.id)
            )
        else:
            neighbors_v4.filter(
                ~Q(id=neighbor.id)
            )

        if not neighbors_v4 and not neighbors_v6:
            if route_map_in.equipments.filter(id=self.equipment.id):
                self.undeploy_route_map(route_map_in)

        neighbors_v4 = NeighborV4.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_out) |
            Q(peer_group__route_map_out=route_map_out))
        ).filter(created=True)

        neighbors_v6 = NeighborV6.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_out) |
            Q(peer_group__route_map_out=route_map_out))
        ).filter(created=True)

        if ip_version == 6:
            neighbors_v6.filter(
                ~Q(id=neighbor.id)
            )
        else:
            neighbors_v4.filter(
                ~Q(id=neighbor.id)
            )

        if not neighbors_v4 and not neighbors_v6:
            if route_map_out.equipments.filter(id=self.equipment.id):
                self.undeploy_route_map(route_map_out)

        # List Config BGP
        if not neighbors_v4 and not neighbors_v6:
            rms = route_map_in.route_map_entries | \
                route_map_out.route_map_entries
            for rm_entry in rms:
                list_config_bgp = rm_entry.list_config_bgp

                neighbors_v6 = NeighborV6.objects.filter(Q(
                    Q(peer_group__route_map_in__route_map_entries__list_config_bgp=list_config_bgp) |
                    Q(peer_group__route_map_out__route_map_entries__list_config_bgp=list_config_bgp))
                ).filter(created=True)

                neighbors_v4 = NeighborV6.objects.filter(Q(
                    Q(peer_group__route_map_in__route_map_entries__list_config_bgp=list_config_bgp) |
                    Q(peer_group__route_map_out__route_map_entries__list_config_bgp=list_config_bgp))
                ).filter(created=True)

                if ip_version == 6:
                    neighbors_v6.filter(
                        ~Q(id=neighbor.id)
                    )
                else:
                    neighbors_v4.filter(
                        ~Q(id=neighbor.id)
                    )

                if not neighbors_v4 and not neighbors_v6:
                    if not list_config_bgp.equipments.filter(id=self.equipment.id):
                        self.undeploy_list_config_bgp(list_config_bgp)

    def deploy_neighbor(self, neighbor):
        """Deploy neighbor"""

        self._deploy_pre_req(neighbor)

        ip_version = IPAddress(str(neighbor.remote_ip)).version

        template_type = self.TEMPLATE_NEIGHBOR_V4_ADD if ip_version == 4 else \
            self.TEMPLATE_NEIGHBOR_V6_ADD

        config = self._generate_template_dict_neighbor(neighbor)

        self._operate_equipment('neighbor', template_type, config)

    def undeploy_neighbor(self, neighbor):
        """Undeploy neighbor"""

        ip_version = IPAddress(str(neighbor.remote_ip)).version

        self._undeploy_pre_req(neighbor, ip_version)

        template_type = self.TEMPLATE_NEIGHBOR_V4_REMOVE \
            if ip_version == 4 else self.TEMPLATE_NEIGHBOR_V6_REMOVE

        config = self._generate_template_dict_neighbor(neighbor)

        self._operate_equipment('neighbor', template_type, config)

    def deploy_list_config_bgp(self, list_config_bgp):
        """Deploy prefix list"""
        log.info("deploy_list_config_bgp")

        config = self._generate_template_dict_list_config_bgp(list_config_bgp)

        self._operate_equipment(
            'list_config_bgp', self.TEMPLATE_LIST_CONFIG_ADD, config)

    def undeploy_list_config_bgp(self, list_config_bgp):
        """Undeploy prefix list"""

        config = self._generate_template_dict_list_config_bgp(list_config_bgp)

        self._operate_equipment(
            'list_config_bgp', self.TEMPLATE_LIST_CONFIG_REMOVE, config)

    def deploy_route_map(self, route_map):
        """Deploy route map"""
        log.info("deploy_route_map")

        config = self._generate_template_dict_route_map(route_map)

        self._operate_equipment(
            'route_map', self.TEMPLATE_ROUTE_MAP_ADD, config)

    def undeploy_route_map(self, route_map):
        """Undeploy route map"""

        config = self._generate_template_dict_route_map(route_map)

        self._operate_equipment(
            'route_map', self.TEMPLATE_ROUTE_MAP_REMOVE, config)

    def _operate_equipment(self, types, template_type, config):

        self.connect()
        self.ensure_privilege_level()
        file_to_deploy = self._generate_config_file(
            types, template_type, config)
        self._deploy_config_in_equipment(file_to_deploy)
        self.close()

    def _generate_config_file(self, types, template_type, config):
        """Load a template and write a file with the rended output.

        Returns: filename with relative path to settings.TFTPBOOT_FILES_PATH
        """

        request_id = getattr(local, 'request_id', NO_REQUEST_ID)

        filename_out = 'bgp_{}_{}_config_{}'.format(
            types, self.equipment.id, request_id)

        filename = BGP_CONFIG_FILES_PATH + filename_out
        rel_file_to_deploy = BGP_CONFIG_TOAPPLY_REL_PATH + filename_out

        config = self._get_template_config(template_type, config)
        self._save_config(filename, config)

        return rel_file_to_deploy

    def _get_template_config(self, template_type, config):
        """Load template file and render values in VARs"""

        try:
            template_file = self._load_template_file(template_type)
            config_to_be_saved = template_file.render(Context(config))

        except KeyError as err:
            log.error('Error: %s', err)
            raise deploy_exc.InvalidKeyException(err)

        except Exception as err:
            log.error('Error: %s ' % err)
            raise self.exceptions.BGPTemplateException(err)
        return config_to_be_saved

    def _load_template_file(self, template_type):
        """Load template file with specific type related to equipment.

        template_type: Type of template to be loaded

        Returns: template string
        """

        equipment_template = self._get_equipment_template(template_type)

        filename = BGP_CONFIG_TEMPLATE_PATH + '/' + equipment_template.roteiro.roteiro

        template_file = self._read_config(filename)

        return template_file

    def _get_equipment_template(self, template_type):
        """Return a script by equipment and template_type"""

        try:
            return eqpt_models.EquipamentoRoteiro.search(
                None, self.equipment.id, template_type).uniqueResult()
        except Exception as e:
            log.error('Template type %s not found. Error: %s' % (template_type, e))
            raise self.exceptions.BGPTemplateException()

    @staticmethod
    def _generate_template_dict_neighbor(neighbor):
        """Make a dictionary to use in template"""

        key_dict = {
            'AS_NUMBER': neighbor.local_asn.name,
            'LOCAL_IP': str(neighbor.local_ip),
            'VRF_NAME': neighbor.remote_ip.networkipv4.vlan.ambiente.default_vrf.internal_name,
            'REMOTE_IP': str(neighbor.remote_ip),
            'REMOTE_AS': neighbor.remote_asn.name,
            'ROUTE_MAP_IN': neighbor.peer_group.route_map_in.name,
            'ROUTE_MAP_OUT': neighbor.peer_group.route_map_out.name,
            'PASSWORD': neighbor.password,
            'TIMER_KEEPALIVE': neighbor.timer_keepalive,
            'TIMER_TIMEOUT': neighbor.timer_timeout,
            'DESCRIPTION': neighbor.description,
            'SOFT_RECONFIGURATION': neighbor.soft_reconfiguration,
            'NEXT_HOP_SELF': neighbor.next_hop_self,
            'REMOVE_PRIVATE_AS': neighbor.remove_private_as,
            'COMMUNITY': neighbor.community,
            'GROUP': "GROUP_{}".format(neighbor.remote_ip)
        }

        return key_dict

    def _generate_template_dict_list_config_bgp(self, list_config_bgp):
        """Make a dictionary to use in template"""

        key_dict = {
            'TYPE': self._get_type_list(list_config_bgp.type)['config_list'],
            'NAME': list_config_bgp.name,
            'CONFIG': list_config_bgp.config
        }

        return key_dict

    def _generate_template_dict_route_map(self, route_map):
        """Make a dictionary to use in template"""

        entries = []

        for entry_obj in route_map.route_map_entries:
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

    @staticmethod
    def _read_config(filename):
        """Return content from template_file"""

        try:
            file_handle = open(filename, 'r')
            template_content = Template(file_handle.read())
            file_handle.close()
        except IOError, e:
            log.error('Error opening template file for read: %s' % filename)
            raise Exception(e)
        except Exception, e:
            log.error('Syntax error when parsing template: %s ' % e)
            raise Exception(e)

        return template_content

    @staticmethod
    def _save_config(filename, config):
        """Write config in template file"""

        try:
            file_handle = open(filename, 'w')
            log.debug(filename)
            file_handle.write(config)
            file_handle.close()
        except IOError, e:
            log.error('Error writing to config file: %s' % filename)
            raise e

    def _deploy_config_in_equipment(self, rel_filename):

        path = os.path.abspath(TFTPBOOT_FILES_PATH + rel_filename)
        if not path.startswith(TFTPBOOT_FILES_PATH):
            raise deploy_exc.InvalidFilenameException(rel_filename)

        return self._apply_config(rel_filename)

    def _apply_config(self, filename):
        log.info("_apply_config")
        if self.equipment.maintenance:
            raise AllEquipmentsAreInMaintenanceException()

        self.copyScriptFileToConfig(filename,
                                    destination='running-config')
