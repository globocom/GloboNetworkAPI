from networkapi.plugins.Dell.FTOS.BGP.Generic import Generic
from networkapi.plugins.factory import PluginFactory
from mock import Mock
from mock import MagicMock

from networkapi.plugins.Dell.FTOS.BGP.exceptions import \
    InvalidNeighborException
from django.test import TestCase


class GenericPluginTestCaseSuccess(TestCase):

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

    def _validate_invalid_neighbor_help(self, neighbor):

        plugin = Generic(neighbor=neighbor)

        with self.assertRaises(InvalidNeighborException):
            plugin._validate_neighbor()

    def test_validate_invalid_neighbors(self):
        """Tests what happens when not valid Neighbors are passed as input."""

        self._validate_invalid_neighbor_help({})
        self._validate_invalid_neighbor_help('')
        self._validate_invalid_neighbor_help(1)
        self._validate_invalid_neighbor_help([])
        self._validate_invalid_neighbor_help({
                                     'remote_ip': '10.10.10.1',
                                     'remote_as': '200',
                                     'soft_reconfiguration': 1})
        self._validate_invalid_neighbor_help({
                                     'remote_ip': '10.10.10.1',
                                     'remote_as': '200',
                                     'community': 1})
        self._validate_invalid_neighbor_help({
                                     'remote_ip': '10.10.10.1',
                                     'remote_as': '200',
                                     'timer_timeout': 'x'})

    def test_treat_soft_reconfiguration_true(self):

        plugin = Generic(neighbor={'soft_reconfiguration': True})

        plugin._treat_soft_reconfiguration()

        self.assertEquals(plugin.neighbor, {'soft_reconfiguration': 'inbound'})

    def test_treat_soft_reconfiguration_false(self):

        plugin = Generic(neighbor={'soft_reconfiguration': False})

        plugin._treat_soft_reconfiguration()

        self.assertEquals(plugin.neighbor, {})

    def test_treat_soft_reconfiguration_without_this_field(self):

        plugin = Generic(neighbor={'remote_ip': '10.10.10.1',
                                   'remote_as': '200'})

        plugin._treat_soft_reconfiguration()

        self.assertEquals(plugin.neighbor, {'remote_ip': '10.10.10.1',
                                            'remote_as': '200'})

    def test_treat_community_true(self):

        plugin = Generic(neighbor={'community': True})

        plugin._treat_community()

        self.assertEquals(plugin.neighbor, {'community': ''})

    def test_treat_community_false(self):

        plugin = Generic(neighbor={'community': False})

        plugin._treat_community()

        self.assertEquals(plugin.neighbor, {})

    def test_treat_community_without_this_field(self):

        plugin = Generic(neighbor={'remote_ip': '10.10.10.1',
                                   'remote_as': '200'})

        plugin._treat_community()

        self.assertEquals(plugin.neighbor, {'remote_ip': '10.10.10.1',
                                            'remote_as': '200'})

    def test_remote_ip_appears_as_a_last_in_generated_ordered_dict(self):

        plugin = Generic(neighbor={'community': True,
                                   'remote_as': '200',
                                   'remote_ip': '10.10.10.1',
                                   'maximum_hops': '10',
                                   'description': 'NAPI'
                                   })

        plugin._order_neighbor()

        neighbor_size = len(plugin.neighbor.items())

        self.assertEquals(('remote_ip', '10.10.10.1'),
                          plugin.neighbor.items()[neighbor_size-1])

    def test_generate_xml_from_valid_dict(self):

        plugin = Generic(neighbor={'remote_as': '200',
                                   'remote_ip': '11.1.1.155',
                                   'password': 'ABC',
                                   'maximum_hops': '5',
                                   'timer_keepalive': '3',
                                   'timer_timeout': '60',
                                   'description': 'desc',
                                   'soft_reconfiguration': True,
                                   'community': True,
                                   'remove_private_as': False,
                                   'next_hop_self': False})

        xml_expected = '<bgp><as-name>65114</as-name><neighbor>' \
                       '<neighbor-router>11.1.1.155</neighbor-router>' \
                       '<timers><keepalive>3</keepalive>' \
                       '<hold-time>60</hold-time></timers>' \
                       '<ebgp-multihop>5</ebgp-multihop>' \
                       '<remote-as>200</remote-as>' \
                       '<password><password-value>' \
                       'ABC</password-value></password>' \
                       '<remove-private-as>false</remove-private-as>' \
                       '<next-hop-self>false</next-hop-self>' \
                       '<send-community />' \
                       '<soft-reconfiguration>inbound</soft-reconfiguration>' \
                       '<description>desc</description></neighbor></bgp>'

        self.assertEquals(plugin._dict_to_xml(), xml_expected)

    def test_generate_xml_from_dict_missing_remote_as(self):

        plugin = Generic(neighbor={'remote_ip': '11.1.1.155',
                                   'password': 'ABC',
                                   'maximum_hops': '5',
                                   'timer_keepalive': '3',
                                   'timer_timeout': '60',
                                   'description': 'desc',
                                   'soft_reconfiguration': True,
                                   'community': True,
                                   'remove_private_as': False,
                                   'next_hop_self': False})

        with self.assertRaises(InvalidNeighborException):
            plugin._dict_to_xml()

    def test_generate_xml_from_dict_missing_remote_ip(self):

        plugin = Generic(neighbor={'remote_as': '200',
                                   'password': 'ABC',
                                   'maximum_hops': '5',
                                   'timer_keepalive': '3',
                                   'timer_timeout': '60',
                                   'description': 'desc',
                                   'soft_reconfiguration': True,
                                   'community': True,
                                   'remove_private_as': False,
                                   'next_hop_self': False})

        with self.assertRaises(InvalidNeighborException):
            plugin._dict_to_xml()

    def test_generate_xml_from_dict_with_next_hop_self_in_wrong_format(self):

        plugin = Generic(neighbor={'remote_as': '200',
                                   'remote_ip': '11.1.1.155',
                                   'password': 'ABC',
                                   'maximum_hops': '5',
                                   'timer_keepalive': '3',
                                   'timer_timeout': '60',
                                   'description': 'desc',
                                   'soft_reconfiguration': True,
                                   'community': True,
                                   'remove_private_as': False,
                                   'next_hop_self': 'false'})

        with self.assertRaises(InvalidNeighborException):
            plugin._dict_to_xml()

    def test_generate_xml_from_dict_with_maximum_hops_in_wrong_format(self):

        plugin = Generic(neighbor={'remote_as': '200',
                                   'remote_ip': '11.1.1.155',
                                   'password': 'ABC',
                                   'maximum_hops': True,
                                   'timer_keepalive': '3',
                                   'timer_timeout': '60',
                                   'description': 'desc',
                                   'soft_reconfiguration': True,
                                   'community': True,
                                   'remove_private_as': False,
                                   'next_hop_self': False})

        with self.assertRaises(InvalidNeighborException):
            plugin._dict_to_xml()

    def test_deploy_neighbor_with_success(self):

        plugin = Generic(neighbor={'remote_as': '200',
                                   'remote_ip': '11.1.1.155',
                                   'password': 'ABC',
                                   'maximum_hops': '5',
                                   'timer_keepalive': '3',
                                   'timer_timeout': '60',
                                   'description': 'desc',
                                   'soft_reconfiguration': True,
                                   'community': True,
                                   'remove_private_as': False,
                                   'next_hop_self': False})




    def test_deploy_neighbor_with_error(self):

        plugin = Generic(neighbor={'remote_as': '200',
                                   'remote_ip': '11.1.1.155',
                                   'password': 'ABC',
                                   'maximum_hops': '5',
                                   'timer_keepalive': '3',
                                   'timer_timeout': '60',
                                   'description': 'desc',
                                   'soft_reconfiguration': True,
                                   'community': True,
                                   'remove_private_as': False,
                                   'next_hop_self': False})

    def test_undeploy_neighbor(self):

        pass



