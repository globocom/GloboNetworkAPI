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
from HTMLParser import HTMLParser

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
            log.info(rm_entry)
            list_config_bgp = rm_entry.list_config_bgp
        #     log.debug(dir(neighbor.peer_group))

        #     if not list_config_bgp.equipments.filter(id=self.equipment.id):
        #         log.info("Deploying list config BGP on equipment. Equipment ID: '%s'." % self.equipment.id)
        #         self.deploy_list_config_bgp(list_config_bgp)

        # # Deploying routemap In on equipment
        # if not route_map_in.equipments.filter(id=self.equipment.id):
        #     log.info("Deploying routemap in on equipment. Equipment ID: '%s'" % self.equipment.id)
        #     self.deploy_route_map(neighbor.peer_group.route_map_in)

        # # Deploying routemap Out on equipment
        # if not route_map_out.equipments.filter(id=self.equipment.id):
        #     log.info("Deploying routemap out on equipment. Equipment ID: '%s'" % self.equipment.id)
        #     self.deploy_route_map(neighbor.peer_group.route_map_out)


    @staticmethod
    def _get_type_list(type_):
        log.info("Getting type list...")

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

        log.info(types[type_])
        return types[type_]

    @staticmethod
    def _read_config(filename):
        """
        Return the content from template_file
        """

        log.info("Reading config from file: '%s'" % filename)

        try:
            file_handle = open(filename, 'r')
            template_content = Template(file_handle.read())

            log.info("Template content:")
            log.info(template_content)

            file_handle.close()
            log.info('File closed.')

        except IOError, e:
            log.error('Error opening template file for read: %s' % filename)
            raise Exception(e)

        except Exception, e:
            log.error('Syntax error when parsing template: %s' % e)
            raise Exception(e)

        return template_content

    @staticmethod
    def _save_config(filename, config):
        """
        Write config in template file
        """

        log.info("Saving config to file.")
        log.info("Filename: %s" % filename)
        log.info("Config: %s" % config)

        try:
            file_handle = open(filename, 'w')
            file_handle.write(config)
            file_handle.close()
            log.info("File closed.")

        except IOError, e:
            log.error('Error writting to config gile: %s' % filename)
            raise e

    @staticmethod
    def _generate_template_dict_neighbor(neighbor):
        """
        Make a dictionary to use in template
        """

        log.info("Generating a template dict to neighbor... Neighbor ID: '%s'" % neighbor.id)

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
            'GROUP': 'GROUP_{}'.format(neighbor.remote_ip)
        }

        log.info(key_dict)

        return key_dict

    def _generate_template_dict_route_map(self, route_map):
        """
        Make a dictionary to use in template
        """
        log.debug(dir(route_map))

        log.info("Generate template dict for routemap. Routemap name: '%s'" % route_map.name)

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

        log.info(key_dict)

        return key_dict

    def _get_equipment_template(self, template_type):
        """
        Return a script by equipment and template_type
        """

        log.info("Getting equipment's template... Template type: '%s'" % template_type)

        try:
            return eqpt_models.EquipamentoRoteiro.search(
                None, self.equipment.id, template_type
            ).uniqueResult()

        except Exception as e:
            log.error('Template type %s not found. Error: %s' %(template_type, e))
            raise self.exceptions.BGPTemplateException()

    def _load_template_file(self, template_type):
        """
        Load template file with specific type related to equipment

        :template_type: Type of template to be loaded

        :returns: template string
        """

        log.info("Loading template file...")

        equipment_template = self._get_equipment_template(template_type=template_type)
        log.info("Equipment's template: '%s'" % equipment_template)

        filename = BGP_CONFIG_TEMPLATE_PATH + '/' + equipment_template.roteiro.roteiro
        log.info("Filename: '%s'" % filename)

        template_file = self._read_config(filename=filename)
        log.info("Template file: '%s'" % template_file)

        return template_file

    def _get_template_config(self, template_type, config):
        """
        Load template file and render values in VARs
        """

        log.info("Getting template config...")

        try:
            template_file = self._load_template_file(template_type=template_type)
            # Instancia o parser para desescapar entidades HTML
            if config.get('CONFIG'):
                converter = HTMLParser()

                # Copia o dicionário e faz o unescape apenas no campo 'CONFIG'
                config['CONFIG'] = converter.unescape(config['CONFIG'])

            config_to_be_saved = template_file.render(Context(config))
            log.info(config_to_be_saved)

        except KeyError as err:
            log.error('Error %s' % err)
            raise deploy_exc.InvalidKeyException(err)

        except Exception as err:
            log.error('Error: %s' % err)
            raise self.exceptions.BGPTemplateException(err)

        return config_to_be_saved

    def _generate_config_file(self, types, template_type, config):
        """
        Load a template and write a file with the rended output

        :returns: filename with relative path to settings.TFTPBOOT_FILES_PATH
        """

        log.info("Generating config file...")

        request_id = getattr(local, 'request_id', NO_REQUEST_ID)

        filename_out = 'bgp_{}_{}_config_{}'.format(
            types, self.equipment.id, request_id
        )

        filename = BGP_CONFIG_FILES_PATH + filename_out
        rel_file_to_deploy = BGP_CONFIG_TOAPPLY_REL_PATH + filename_out

        log.info("Filename: '%s'" % filename)
        log.info("Relative file to deploy: '%s'" % rel_file_to_deploy)

        config = self._get_template_config(template_type=template_type, config=config)
        log.info("Config generated successfully.")

        self._save_config(filename=filename, config=config)
        log.info("Config saved successfully.")

        return rel_file_to_deploy

    def _apply_config(self, filename):

        log.info("_apply_config")

        if self.equipment.maintenance:
            raise AllEquipmentsAreInMaintenanceException()

        self.copyScriptFileToConfig(filename=filename, destination='running-config')
        log.info("Configuration in file: '%s' successfully applyied on equipment" % filename)

    def _deploy_config_in_equipment(self, rel_filename):

        log.info("Deploying config on equipment. Relative filename: '%s'." % rel_filename)

        path = os.path.abspath(TFTPBOOT_FILES_PATH + rel_filename)

        if not path.startswith(TFTPBOOT_FILES_PATH):
            raise deploy_exc.InvalidFilenameException(rel_filename)

        return self._apply_config(filename=rel_filename)

    def _operate_equipment(self, types, template_type, config):

        log.info("Operate equipment method...")

        self.connect()

        file_to_deploy = self._generate_config_file(
            types=types, template_type=template_type, config=config
        )
        log.info("Configuration file generated successfully")

        self._deploy_config_in_equipment(file_to_deploy)
        log.info("Configuration deployed on equipment successfully")

        self.close()
        log.info("Connection closed successfully.")

    def _generate_template_dict_list_config_bgp(self, list_config_bgp):
        """
        Make a dictionary to use in template
        """

        log.info("_generate_template_dict_list_config_bgp")

        key_dict = {
            'TYPE': self._get_type_list(list_config_bgp.type)['config_list'],
            'NAME': list_config_bgp.name,
            'CONFIG': list_config_bgp.config
        }

        log.info(key_dict)

        return key_dict

    def _undeploy_pre_req(self, neighbor, ip_version):

        log.info("_undeploy_pre_req")

        # Concatenate RouteMapEntries Lists
        route_map_in = neighbor.peer_group.route_map_in
        route_map_out = neighbor.peer_group.route_map_out

        neighbors_v4 = NeighborV4.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_in) |
            Q(peer_group__route_map_out=route_map_in)
        )).filter(created=True)

        neighbors_v6 = NeighborV6.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_in) |
            Q(peer_group__route_map_out=route_map_in)
        )).filter(created=True)

        neighbors_v4 = neighbors_v4.exclude(Q(id=neighbor.id))
        neighbors_v6 = neighbors_v6.exclude(Q(id=neighbor.id))

        log.info("Neighbors V4: '%s'." % neighbors_v4)
        log.info("Neighbors V6: '%s'." % neighbors_v6)

        if not neighbors_v4 and not neighbors_v6:
            log.info("No neighbors founded...")
            try:
                self.undeploy_route_map(route_map_in)
                log.info("Routemap '%s' undeployed successfully." % route_map_in)

            except Exception as e:
                log.error("Error while undeploying route-map. Error: {}".format(e))

        neighbors_v4 = NeighborV4.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_out) |
            Q(peer_group__route_map_out=route_map_out)
        )).filter(created=True)

        neighbors_v6 = NeighborV6.objects.filter(Q(
            Q(peer_group__route_map_in=route_map_out) |
            Q(peer_group__route_map_out=route_map_out)
        )).filter(created=True)

        neighbors_v4 = neighbors_v4.exclude(Q(id=neighbor.id))
        neighbors_v6 = neighbors_v6.exclude(Q(id=neighbor.id))

        log.info("Neighbors V4: '%s'." % neighbors_v4)
        log.info("Neighbors V6: '%s'." % neighbors_v6)

        if not neighbors_v4 and not neighbors_v6:
            log.info("No neighbors founded...")
            try:
                self._undeploy_route_map(route_map=route_map_out)
                log.info("Routemap '%s' undeployed successfully." % route_map_out)

            except Exception as e:
                log.error("Error while undeploying route-map. Error: {}".format(e))

        # List Config BGP
        if not neighbors_v4 and not neighbors_v6:
            rms = route_map_in.route_map_entries | \
                route_map_out.route_map_entries

            for rm_entry in rms:
                list_config_bgp = rm_entry.list_config_bgp
                log.info("List config BGP: '%s'." % list_config_bgp)

                neighbors_v4 = NeighborV4.objects.filter(Q(
                    Q(peer_group__route_map_in__routemapentry__list_config_bgp=list_config_bgp) |
                    Q(peer_group__route_map_out__routemapentry__list_config_bgp=list_config_bgp)
                )).filter(created=True)

                neighbors_v6 = NeighborV6.objects.filter(Q(
                    Q(peer_group__route_map_in__routemapentry__list_config_bgp=list_config_bgp) |
                    Q(peer_group__route_map_out__routemapentry__list_config_bgp=list_config_bgp)
                )).filter(created=True)

                neighbors_v4 = neighbors_v4.exclude(Q(id=neighbor.id))
                neighbors_v6 = neighbors_v6.exclue(Q(id=neighbor.id))

                log.info("Neighbors V4: '%s'." % neighbors_v4)
                log.info("Neighbors V6: '%s'." % neighbors_v6)

                if not neighbors_v4 and not neighbors_v6:
                    log.info("No neighbors founded...")
                    try:
                        self.undeploy_list_config_bgp(list_config_bgp=list_config_bgp)
                        log.info("List config BGP '%s' undeployed successfully." % list_config_bgp)

                    except Exception as e:
                        log.error("Error while undeploying prefix-list. Error: {}".format(e))

    def _operate(self, types, template_type, config):

        log.info("_operate method")

        file_to_deploy = self._generate_config_file(
            types=types,
            template_type=template_type,
            config=config
        )

        log.info("File to Deploy: '%s'." % file_to_deploy)

        self._deploy_config_in_equipment(rel_filename=file_to_deploy)
        log.info("Configuration successfully deployed on equipment.")

        self.close()
        log.info("Netconf session closed.")

    def _undeploy_route_map(self, route_map):
        """
        Undeploy route map
        """

        log.info("Undelpoy routemap method started... Routemap: '%s'" % route_map)

        config = self._generate_template_dict_route_map(route_map=route_map)
        log.info("Configuration successfully generated.")

        self._operate(
            types='route_map',
            template_type=self.TEMPLATE_ROUTE_MAP_REMOVE,
            config=config
        )

    def _open(self):

        log.info("Openning Netconf session...")
        self.connect()
        log.info("Session openned succesfully.")

    def undeploy_neighbor(self, neighbor):
        """
        Undeploy neighbor
        """

        log.info("Undeploy neighbor method started... Neighbor: '%s'" % neighbor)

        ip_version = IPAddress(str(neighbor.remote_ip)).version

        template_type = self.TEMPLATE_NEIGHBOR_V4_REMOVE \
            if ip_version == 4 else self.TEMPLATE_NEIGHBOR_V6_REMOVE

        log.info("Template type: '%s'." % template_type)

        config = self._generate_template_dict_neighbor(neighbor=neighbor)
        log.info("Configuration dict generated successfuly. Config: '%s'" % config)

        self._open()
        self._operate(
            types='neighbor',
            template_type=template_type,
            config=config
        )

        self._undeploy_pre_req(
            neighbor=neighbor,
            ip_version=ip_version
        )
        log.info("Pre req undeployed successfully.")

        self.close()

    def deploy_list_config_bgp(self, list_config_bgp):
        """
        Deploy prefix list
        """

        log.info("Deploy list config BGP method started... List Config BGP: '%s'." % list_config_bgp)

        config = self._generate_template_dict_list_config_bgp(list_config_bgp=list_config_bgp)
        log.info("Dict list config BGP generated successfully. Config: '%s'" % config)

        self._operate_equipment(
            types='list_config_bgp',
            template_type=self.TEMPLATE_LIST_CONFIG_ADD,
            config=config
        )
        log.info("List config BGP successfully deployed.")

    def deploy_route_map(self, route_map):
        """
        Deploy route map
        """

        log.info("Deploy route map method started...")

        config = self._generate_template_dict_route_map(route_map)
        log.info("Dict config for routemap created successfully... Config: '%s'" % config)

        self._operate_equipment(
            'route_map', self.TEMPLATE_ROUTE_MAP_ADD, config
        )
        log.info("Routemap successfully deployed.")

    def undeploy_list_config_bgp(self, list_config_bgp):
        """
        Undeploy prefix list
        """

        log.info("Undeploy list config BGP method started.")

        config = self._generate_template_dict_list_config_bgp(list_config_bgp=list_config_bgp)
        log.info("Dict for list config BGP created. Config: '%s'" % config)

        self._operate_equipment(
            types='list_config_bgp',
            template_type=self.TEMPLATE_LIST_CONFIG_REMOVE,
            config=config
        )
        log.info("List config BGP successfully undeployed.")

    def deploy_neighbor(self, neighbor):
        """
        Deploy neighbor
        """

        log.info("Deploy neighbor method started...")

        self._deploy_pre_req(neighbor=neighbor)
        log.info("Pre req successfully deployed...")

        ip_version = IPAddress(str(neighbor.remote_ip)).version

        template_type = self.TEMPLATE_NEIGHBOR_V4_ADD if ip_version == 4 else \
            self.TEMPLATE_NEIGHBOR_V6_ADD
        log.info("Template type: '%s'." % template_type)

        config = self._generate_template_dict_neighbor(neighbor=neighbor)
        log.info("Dict for neighbor config successfully generated. Config: '%s'" % config)

        self._operate_equipment(
            types='neighbor',
            template_type=template_type,
            config=config
        )
        log.info("Neighbor deployed successfully.")

    def undeploy_route_map(self, route_map):
        """
        Undeply route map
        """

        log.info("Undeploy routemap method started...")

        config = self._generate_template_dict_route_map(route_map=route_map)
        log.info("Dict for routemap config generated successfully. Config: '%s'" % config)

        self._operate(
            types='route_map',
            template_type=self.TEMPLATE_ROUTE_MAP_REMOVE,
            config=config
        )
        log.info("Routemap deployed successfully.")

    def _close(self):
        log.info("Close connection method started")
        self.close()
        log.info("Connection closed successfully.")

