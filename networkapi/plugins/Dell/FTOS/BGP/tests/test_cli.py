from networkapi.plugins.Dell.FTOS.BGP.Cli import Generic
from networkapi.plugins.factory import PluginFactory
from mock import Mock
from mock import MagicMock

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

        asn = {'name': '65114'}
        vrf = {'vrf': 'BEVrf'}

        self._generate_config_helper_add(neighbor, asn, vrf,
                                         'template_neighbor_v4_add_dell')

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

        asn = {'name': '65114'}
        vrf = {'vrf': 'BEVrf'}

        self._generate_config_helper_add(neighbor, asn, vrf,
                                         'template_neighbor_v6_add_dell')

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

        asn = {'name': '65114'}
        vrf = {'vrf': 'BEVrf'}

        self._generate_config_helper_remove(neighbor, asn, vrf,
                                            'template_neighbor_v4_remove_dell')

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

        asn = {'name': '65114'}
        vrf = {'vrf': 'BEVrf'}

        self._generate_config_helper_remove(neighbor, asn, vrf,
                                            'template_neighbor_v6_remove_dell')

    def _mock_equipment(self):

        equipment = Mock()
        marca = MagicMock(nome='DELL')
        equipment.modelo = MagicMock(nome='FTOS', marca=marca)
        equipment.maintenance = False

        return equipment

    def _mock_roteiro(self, roteiro):

        roteiro_str = MagicMock(roteiro=roteiro)
        roteiro_mock = MagicMock(roteiro=roteiro_str)

        return Mock(return_value=roteiro_mock)

    def _mock_plugin(self, plugin):

        plugin.connect = MagicMock()
        plugin._ensure_privilege_level = MagicMock()
        plugin.close = MagicMock()
        plugin._copy_script_file_to_config = MagicMock()

        return plugin

    def _generate_config_helper_add(self, neighbor, asn, vrf, roteiro):

        plugin = Generic(equipment=self._mock_equipment(), neighbor=neighbor,
                         asn=asn, vrf=vrf)
        plugin = self._mock_plugin(plugin)

        plugin._get_equipment_template = self._mock_roteiro(roteiro)

        plugin.deploy_neighbor()

    def _generate_config_helper_remove(self, neighbor, asn, vrf, roteiro):
        plugin = Generic(equipment=self._mock_equipment(), neighbor=neighbor,
                         asn=asn, vrf=vrf)
        plugin = self._mock_plugin(plugin)

        plugin._get_equipment_template = self._mock_roteiro(roteiro)

        plugin.undeploy_neighbor()