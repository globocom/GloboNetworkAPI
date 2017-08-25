from networkapi.plugins.Dell.FTOS.BGP.Cli import Generic
from networkapi.plugins.factory import PluginFactory
from mock import Mock
from mock import MagicMock
from random import randint

from django.test import TestCase

class CliPluginTestCaseSuccess(TestCase):

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

    def test_generate_config_for_neighbor_v4_add(self):

        neighbor = {'remote_as': '200',
                    'remote_ip': '11.1.1.155',
                    'password': 'ABC',
                    'maximum_hops': '5',
                    'timer_keepalive': '3',
                    'timer_timeout': '60',
                    'description': 'desc',
                    'soft_reconfiguration': True,
                    'community': True,
                    'remove_private_as': False,
                    'next_hop_self': False}

        asn = {'name': '25114'}
        vrf = {'vrf': 'Vrf-Test'}
        virtual_interface = {'name': 'VirtInt-Test'}

        # self._generate_config_helper_add(neighbor, virtual_interface, asn, vrf,
        #                                  'template_neighbor_v4_add_cisco')

    def test_generate_config_for_neighbor_v6_add(self):

        neighbor = {'remote_as': '200',
                    'remote_ip': 'fdac:3801:79b9:b96c:0:0:0:1',
                    'password': 'ABC',
                    'maximum_hops': '5',
                    'timer_keepalive': '3',
                    'timer_timeout': '60',
                    'description': 'desc',
                    'soft_reconfiguration': True,
                    'community': True,
                    'remove_private_as': False,
                    'next_hop_self': False}

        asn = {'name': '25114'}
        vrf = {'vrf': 'Vrf-Test'}
        virtual_interface = {'name': 'VirtInt-Test'}

        # self._generate_config_helper_add(neighbor, virtual_interface, asn, vrf,
        #                                  'template_neighbor_v6_add_cisco')

    def test_generate_config_for_neighbor_v4_remove(self):

        neighbor = {'remote_as': '200',
                    'remote_ip': '11.1.1.155',
                    'password': 'ABC',
                    'maximum_hops': '5',
                    'timer_keepalive': '3',
                    'timer_timeout': '60',
                    'description': 'desc',
                    'soft_reconfiguration': True,
                    'community': True,
                    'remove_private_as': False,
                    'next_hop_self': False}

        asn = {'name': '25114'}
        vrf = {'vrf': 'Vrf-Test'}
        virtual_interface = {'name': 'VirtInt-Test'}

        # self._generate_config_helper_remove(neighbor, virtual_interface, asn, vrf,
        #                                     'template_neighbor_v4_remove_cisco')

    def test_generate_config_for_neighbor_v6_remove(self):

        neighbor = {'remote_as': '200',
                    'remote_ip': 'fdac:3801:79b9:b96c:0:0:0:1',
                    'password': 'ABC',
                    'maximum_hops': '5',
                    'timer_keepalive': '3',
                    'timer_timeout': '60',
                    'description': 'desc',
                    'soft_reconfiguration': True,
                    'community': True,
                    'remove_private_as': False,
                    'next_hop_self': False}

        asn = {'name': '25114'}
        vrf = {'vrf': 'Vrf-Test'}
        virtual_interface = {'name': 'VirtInt-Test'}

        # self._generate_config_helper_remove(neighbor, virtual_interface, asn, vrf,
        #                                     'template_neighbor_v6_remove_cisco')

    def _mock_equipment(self):

        equipment = Mock()
        marca = MagicMock(nome='CISCO')
        equipment.modelo = MagicMock(nome='NXOS', marca=marca)
        equipment.maintenance = False
        equipment.id = randint(0,100000)

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

    def _generate_config_helper_add(self, neighbor, virtual_interface,
                                    asn, vrf, roteiro):

        plugin = Generic(equipment=self._mock_equipment(),
                         virtual_interface=virtual_interface,
                         neighbor=neighbor, asn=asn, vrf=vrf)
        plugin = self._mock_plugin(plugin, roteiro)

        template_name = plugin._get_template_deploy_name()
        file_to_deploy = plugin._generate_config_file(template_name)

    def _generate_config_helper_remove(self, neighbor, virtual_interface,
                                       asn, vrf, roteiro):

        plugin = Generic(equipment=self._mock_equipment(),
                         virtual_interface=virtual_interface,
                         neighbor=neighbor, asn=asn, vrf=vrf)
        plugin = self._mock_plugin(plugin, roteiro)

        template_name = plugin._get_template_undeploy_name()
        file_to_deploy = plugin._generate_config_file(template_name)
