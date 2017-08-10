from networkapi.plugins.Dell.FTOS.BGP.Generic import Generic
from networkapi.plugins.factory import PluginFactory
from mock import Mock, MagicMock

from networkapi.plugins.Dell.FTOS.BGP.exceptions import \
    InvalidNeighborException
from django.test import TestCase


class GenericPluginTestCaseSuccess(TestCase):

    def test_json_to_xml(self):

        pass

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

    def _mock_equipment(self):
        equipment = Mock()
        marca = MagicMock(nome='DELL')
        equipment.modelo = MagicMock(nome='FTOS', marca=marca)

        return equipment

    def test_treat_neighbor_invalid(self):
        """Tests what happens when not valid Neighbors are passed as input."""

        self.treat_neighbor_help({})
        self.treat_neighbor_help('')
        self.treat_neighbor_help(1)
        self.treat_neighbor_help([])

    def treat_neighbor_help(self, neighbor):

        plugin = Generic(neighbor=neighbor)

        with self.assertRaises(InvalidNeighborException):
            plugin._process_neighbor()

    def test_treat_soft_reconfiguration_true(self):

        plugin = Generic(neighbor={'soft_reconfiguration': True})

        plugin._treat_soft_reconfiguration()

        self.assertEquals(plugin.neighbor, {'soft_reconfiguration': 'inbound'})

    def test_treat_soft_reconfiguration_false(self):

        plugin = Generic(neighbor={'soft_reconfiguration': False})

        plugin._treat_soft_reconfiguration()

        self.assertEquals(plugin.neighbor, {})

    def test_treat_community_true(self):

        plugin = Generic(neighbor={'community': True})

        plugin._treat_community()

        self.assertEquals(plugin.neighbor, {'community': ''})

    def test_treat_community_false(self):

        plugin = Generic(neighbor={'community': False})

        plugin._treat_community()

        self.assertEquals(plugin.neighbor, {})

    def test_treat_neighbor_without_soft_reconfiguration(self):

        plugin = Generic(neighbor={'remote_ip': '10.10.10.1'})

        plugin._process_neighbor()

        self.assertEquals(plugin.neighbor, {'remote_ip': '10.10.10.1'})

    def test_treat_neighbor_with_invalid_soft_reconfiguration(self):

        self.treat_neighbor_help(
            {'remote_ip': '10.10.10.1', 'soft_reconfiguration': 1})

    def test_treat_neighbor_with_invalid_community(self):

        self.treat_neighbor_help({'remote_ip': '10.10.10.1', 'community': 1})








