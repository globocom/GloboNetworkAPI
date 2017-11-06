# -*- coding: utf-8 -*-
"""
   Copyright 2017 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import os
from random import randint

from django.test import TestCase
from mock import MagicMock
from mock import Mock

from networkapi.plugins.Dell.FTOS.BGP.Cli import Generic
from networkapi.plugins.factory import PluginFactory


class CliPluginTestCaseSuccess(TestCase):

    def setUp(self):

        self.ipv4_neighbor = {
            'remote_as': '200',
            'remote_ip': '11.1.1.155',
            'password': 'ABC',
            'maximum_hops': '5',
            'timer_keepalive': '3',
            'timer_timeout': '60',
            'description': 'desc',
            'soft_reconfiguration': True,
            'community': True,
            'remove_private_as': False,
            'next_hop_self': False
        }

        self.ipv6_neighbor = {
            'remote_as': '200',
            'remote_ip': 'fdac:3801:79b9:b96c:0:0:0:1',
            'password': 'ABC',
            'maximum_hops': '5',
            'timer_keepalive': '3',
            'timer_timeout': '60',
            'description': 'desc',
            'soft_reconfiguration': True,
            'community': True,
            'remove_private_as': False,
            'next_hop_self': False
        }

        self.asn = {'name': '25114'}
        self.vrf = {'vrf': 'Vrf-Test'}
        self.virtual_interface = {'name': 'VirtInt-Test'}

        self.fake_template_v4_path = 'networkapi/plugins/Dell/FTOS/BGP/' \
                                     'tests/configs/config_v4_dell'

        self.fake_template_v6_path = 'networkapi/plugins/Dell/FTOS/BGP/' \
                                     'tests/configs/config_v6_dell'

    def test_factory_bgp(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        self.assertEqual(hasattr(plugin, 'bgp'), True)

    def test_factory_bgp_deploy_neighbor(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(hasattr(plugin.bgp(neighbor), 'deploy_neighbor'),
                         True)

    def test_factory_bgp_undeploy_neighbor(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(hasattr(plugin.bgp(neighbor), 'undeploy_neighbor'),
                         True)

    def test_generate_template_dict_for_ipv4_neighbor(self):

        plugin = Generic(equipment=self._mock_equipment(),
                         virtual_interface=self.virtual_interface,
                         neighbor=self.ipv4_neighbor, asn=self.asn,
                         vrf=self.vrf)

        returned_dict = plugin._generate_template_dict()

        expected_dict = {
            'AS_NUMBER': '25114',
            'VRF_NAME': 'Vrf-Test',
            'REMOTE_IP': '11.1.1.155',
            'REMOTE_AS': '200',
            'PASSWORD': 'ABC',
            'TIMER_KEEPALIVE': '3',
            'TIMER_TIMEOUT': '60',
            'DESCRIPTION': 'desc',
            'SOFT_RECONFIGURATION': True,
            'COMMUNITY': True,
            'REMOVE_PRIVATE_AS': False,
            'NEXT_HOP_SELF': False
        }

        self.assertDictEqual(expected_dict, returned_dict)

    def test_get_deploy_template_name_for_ipv4_neighbor(self):

        self._helper_to_check_templates_name(
            'deploy', self.ipv4_neighbor, 'neighbor_v4_add')

    def test_get_deploy_template_name_for_ipv6_neighbor(self):

        self._helper_to_check_templates_name(
            'deploy', self.ipv6_neighbor, 'neighbor_v6_add')

    def test_get_undeploy_template_name_for_ipv4_neighbor(self):

        self._helper_to_check_templates_name(
            'undeploy', self.ipv4_neighbor, 'neighbor_v4_remove')

    def test_get_undeploy_template_name_for_ipv6_neighbor(self):

        self._helper_to_check_templates_name(
            'undeploy', self.ipv6_neighbor, 'neighbor_v6_remove')

    def test_generate_config_for_neighbor_v4_add(self):

        self._generate_config_helper(
            'deploy', self.ipv4_neighbor, self.virtual_interface,
            self.asn, self.vrf, 'template_neighbor_v4_add_dell')

    def test_generate_config_for_neighbor_v6_add(self):

        self._generate_config_helper(
            'deploy', self.ipv6_neighbor, self.virtual_interface,
            self.asn, self.vrf, 'template_neighbor_v6_add_dell')

    def test_generate_config_for_neighbor_v4_remove(self):

        self._generate_config_helper(
            'undeploy', self.ipv4_neighbor, self.virtual_interface,
            self.asn, self.vrf, 'template_neighbor_v4_remove_dell')

    def test_generate_config_for_neighbor_v6_remove(self):

        self._generate_config_helper(
            'undeploy', self.ipv6_neighbor, self.virtual_interface,
            self.asn, self.vrf, 'template_neighbor_v6_remove_dell')

    def _mock_equipment(self):

        equipment = Mock()
        marca = MagicMock(nome='DELL')
        equipment.modelo = MagicMock(nome='FTOS', marca=marca)
        equipment.maintenance = False
        equipment.id = randint(0, 100000)

        return equipment

    def _mock_roteiro(self, roteiro):

        roteiro_str = MagicMock(roteiro=roteiro)
        roteiro_mock = MagicMock(roteiro=roteiro_str)

        return Mock(return_value=roteiro_mock)

    def _mock_plugin(self, plugin, roteiro):

        plugin.connect = MagicMock()
        plugin._ensure_privilege_level = MagicMock()
        plugin.close = MagicMock()
        plugin._copy_script_file_to_config = MagicMock()
        plugin._get_equipment_template = self._mock_roteiro(roteiro)

        return plugin

    def _helper_to_check_templates_name(self, type_operation, neighbor,
                                        expected_template_name):

        plugin = Generic(equipment=self._mock_equipment(),
                         virtual_interface=self.virtual_interface,
                         neighbor=neighbor, asn=self.asn,
                         vrf=self.vrf)

        if type_operation == 'deploy':
            returned_template_name = plugin._get_template_deploy_name()
        elif type_operation == 'undeploy':
            returned_template_name = plugin._get_template_undeploy_name()

        self.assertEquals(expected_template_name,
                          returned_template_name)

    def _generate_config_helper(self, type_operation, neighbor,
                                virtual_interface, asn, vrf, roteiro):

        plugin = Generic(equipment=self._mock_equipment(),
                         virtual_interface=virtual_interface,
                         neighbor=neighbor, asn=asn, vrf=vrf)
        plugin = self._mock_plugin(plugin, roteiro)

        if type_operation == 'deploy':
            template_name = plugin._get_template_deploy_name()
        elif type_operation == 'undeploy':
            template_name = plugin._get_template_undeploy_name()

        path_file_to_deploy = plugin._generate_config_file(template_name)

        if 'v4' in roteiro:
            fake_dell = self._get_file_content(self.fake_template_v4_path,
                                               False)
        elif 'v6' in roteiro:
            fake_dell = self._get_file_content(self.fake_template_v6_path,
                                               False)

        file_to_deploy = self._get_file_content(path_file_to_deploy, True)

        self.assertEquals(fake_dell, file_to_deploy)

    def _get_file_content(self, path, delete_after):

        with open(path, 'r') as f:
            content = f.read()

        try:
            if delete_after:
                os.remove(path)
        except OSError:
            pass

        return content
