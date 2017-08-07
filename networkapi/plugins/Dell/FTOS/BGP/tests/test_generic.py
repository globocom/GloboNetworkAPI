from networkapi.plugins.Dell.FTOS.BGP.Generic import Generic
from networkapi.plugins.factory import PluginFactory
from networkapi.equipamento.models import Equipamento
from mock import Mock, MagicMock

from django.test import TestCase


class GenericPluginTestCaseSuccess(TestCase):

    def test_json_to_xml(self):

        Generic().json_to_xml()

    def test_factory_bgp(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)
        self.assertEqual(hasattr(plugin, 'bgp'), True)

    def test_factory_bgp_deploy_neighbor(self):
        equipment = self._mock_equipment()
        plugin = PluginFactory.factory(equipment)

        import ipdb; ipdb.sset_trace()
        self.assertEqual(hasattr(plugin.bgp(), 'deploy_neighbor'), True)


    def _mock_equipment(self):
        equipment = Mock()
        marca = MagicMock(nome='DELL')
        equipment.modelo = MagicMock(nome='FTOS', marca=marca)

        return equipment
