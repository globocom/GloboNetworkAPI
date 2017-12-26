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
from mock import patch

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

    def test_undeploy_route_map(self):
        undeploy_route_map_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic().undeploy_route_map()

        undeploy_route_map_mock.assert_called_once_with('route_map_remove')

    def test_deploy_route_map(self):
        undeploy_route_map_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic().deploy_route_map()

        undeploy_route_map_mock.assert_called_once_with('route_map_add')

    def test_deploy_neighbor_v4(self):
        deploy_neighbor_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic(neighbor={'remote_ip': '1.1.1.1'}).deploy_neighbor()

        deploy_neighbor_mock.assert_called_once_with('neighbor_v4_add')

    def test_undeploy_neighbor_v4(self):
        undeploy_neighbor_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic(neighbor={'remote_ip': '1.1.1.1'}).undeploy_neighbor()

        undeploy_neighbor_mock.assert_called_once_with('neighbor_v4_remove')

    def test_deploy_neighbor_v6(self):
        deploy_neighbor_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic(neighbor={'remote_ip': '1:1:1:1:1:1:1:1'}).deploy_neighbor()

        deploy_neighbor_mock.assert_called_once_with('neighbor_v6_add')

    def test_undeploy_neighbor_v6(self):
        undeploy_neighbor_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic(neighbor={'remote_ip': '1:1:1:1:1:1:1:1'}).undeploy_neighbor()

        undeploy_neighbor_mock.assert_called_once_with('neighbor_v6_remove')

    def test_deploy_prefix_list(self):
        deploy_prefix_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic().deploy_prefix_list()

        deploy_prefix_mock.assert_called_once_with('prefix_list_add')

    def test_undeploy_prefix_list(self):
        undeploy_prefix_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.Generic._operate_equipment'
        ).start()

        Generic().undeploy_prefix_list()

        undeploy_prefix_mock.assert_called_once_with('prefix_list_remove')

    def test_factory_bgp(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        self.assertEqual(hasattr(plugin, 'bgp'), True)

    def test_factory_bgp_undeploy_route_map(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(
            hasattr(plugin.bgp(neighbor), 'undeploy_route_map'), True)

    def test_factory_bgp_deploy_route_map(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(
            hasattr(plugin.bgp(neighbor), 'deploy_route_map'), True)

    def test_factory_bgp_deploy_neighbor(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(
            hasattr(plugin.bgp(neighbor), 'deploy_neighbor'), True)

    def test_factory_bgp_undeploy_neighbor(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(
            hasattr(plugin.bgp(neighbor), 'undeploy_neighbor'), True)

    def test_factory_bgp_deploy_prefix_list(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(
            hasattr(plugin.bgp(neighbor), 'deploy_prefix_list'), True)

    def test_factory_bgp_undeploy_prefix_list(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        neighbor = {}

        self.assertEqual(
            hasattr(plugin.bgp(neighbor), 'undeploy_prefix_list'), True)

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

    def test_wait_string(self):

        plugin = Generic()

        plugin.channel = Mock()
        plugin.channel.recv.side_effect = ['test', 'ok']

        string = plugin._wait_string('ok')

        self.assertEqual(plugin.channel.recv.call_count, 2)
        self.assertEqual(string, 'ok')

    def test_wait_string_sleep(self):
        sleep_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.sleep').start()

        plugin = Generic()

        plugin.channel = Mock()
        plugin.channel.recv.side_effect = ['ok']
        plugin.channel.recv_ready.side_effect = [False, True]

        plugin._wait_string('ok')

        sleep_mock.assert_called_once_with(1)
        self.assertEqual(sleep_mock.call_count, 1)

    def test_wait_string_2_sleep(self):

        sleep_mock = patch(
            'networkapi.plugins.Dell.FTOS.BGP.Cli.sleep').start()

        plugin = Generic()

        plugin.channel = Mock()
        plugin.channel.recv.side_effect = ['ok']
        plugin.channel.recv_ready.side_effect = [False, False, True]

        plugin._wait_string('ok')

        sleep_mock.assert_called_with(1)
        self.assertEqual(sleep_mock.call_count, 2)

    def test_copy_script_file_to_config(self):

        plugin = Generic()
        plugin.tftpserver = '1.1.1.1'

        plugin.channel = Mock()
        plugin.channel.recv.side_effect = ['bytes successfully copied']

        plugin._copy_script_file_to_config(
            filename='filename', use_vrf='VRFBE', destination='running-config')

        # sleep
        plugin.channel.send.assert_called_once_with(
            'copy tftp://1.1.1.1/filename running-config VRFBE\n\n\n')

    #########
    # MOCKS #
    #########
    def _mock_equipment(self):

        equipment = Mock()
        marca = MagicMock(nome='DELL')
        equipment.modelo = MagicMock(nome='FTOS', marca=marca)
        equipment.maintenance = False
        equipment.id = randint(0, 100000)

        return equipment
