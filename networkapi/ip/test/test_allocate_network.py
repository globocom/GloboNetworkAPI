# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from mock import Mock
from mock import patch

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import ConfigEnvironment
from networkapi.ambiente.models import ConfigEnvironmentInvalidError
from networkapi.ambiente.models import EnvironmentVip
from networkapi.ambiente.models import IP_VERSION
from networkapi.ambiente.models import IPConfig
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4AddressNotAvailableError
from networkapi.usuario.models import Usuario
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanNotFoundError


class NetworkAddTestCase(unittest.TestCase):

    def setUp(self):
        self.user = Usuario()
        self.vlan = Vlan(id=1, ambiente=Ambiente(id=1))
        self.network_type = TipoRede(id=1)
        self.vip_env = EnvironmentVip(id=1)
        self.network = NetworkIPv4(oct1=10, oct2=126, oct3=1, oct4=0, block=24)

        self.mock_distributed_lock()
        self.mock_transaction()

    def tearDown(self):
        patch.stopall()

    def test_add_network_ipv4_given_vlan_not_found(self):
        self.mock_find_vlan_by_pk(VlanNotFoundError(''))

        with self.assertRaises(VlanNotFoundError):
            network = NetworkIPv4()
            network.add_network_ipv4(
                self.user, 2, self.network_type, self.vip_env, 24)

    def test_add_network_ipv4_given_environment_config_not_found(self):
        self.mock_find_vlan_by_pk(self.vlan)
        self.mock_find_config_environment([])

        with self.assertRaises(ConfigEnvironmentInvalidError):
            network = NetworkIPv4()
            network.add_network_ipv4(
                self.user, self.vlan.id, self.network_type, self.vip_env, 24)
            self.assertEquals(self.vlan, network.vlan)

    def test_add_network_ipv4_given_no_ipv4_config_set(self):
        self.mock_find_vlan_by_pk(self.vlan)
        self.mock_find_config_environment(
            [ConfigEnvironment(ip_config=IPConfig(type=IP_VERSION.IPv6[0]))])
        self.mock_get_networks([self.network])

        with self.assertRaises(ConfigEnvironmentInvalidError):
            network = NetworkIPv4()
            network.add_network_ipv4(
                self.user, self.vlan.id, self.network_type, self.vip_env, 24)
            self.assertEquals(self.vlan, network.vlan)

    def test_add_network_ipv4_given_no_more_address_available(self):
        environment_config = ConfigEnvironment(ip_config=IPConfig(
            type=IP_VERSION.IPv4[0], subnet='10.126.1.0/24'))
        self.mock_find_vlan_by_pk(self.vlan)
        self.mock_find_config_environment([environment_config])
        self.mock_get_networks([self.network])

        with self.assertRaises(NetworkIPv4AddressNotAvailableError):
            network = NetworkIPv4()
            network.add_network_ipv4(
                self.user, self.vlan.id, self.network_type, self.vip_env, 24)
            self.assertEquals(self.vlan, network.vlan)

    def test_add_network_ipv4_successfully(self):
        environment_config = ConfigEnvironment(ip_config=IPConfig(
            type=IP_VERSION.IPv4[0], subnet='10.126.1.0/24'))
        self.mock_find_vlan_by_pk(self.vlan)
        self.mock_find_config_environment([environment_config])
        self.mock_get_networks([])
        save_network_mock = self.mock_save_network()

        network = NetworkIPv4()
        vlan_map = network.add_network_ipv4(
            self.user, self.vlan.id, self.network_type, self.vip_env, 24)
        self.assertEquals(self.vlan, network.vlan)
        self.assertTrue(save_network_mock.called)
        self.assertTrue(isinstance(vlan_map, dict))

    def mock_find_vlan_by_pk(self, response):
        mock = patch('networkapi.vlan.models.Vlan.get_by_pk').start()
        if issubclass(response.__class__, Exception):
            mock.side_effect = response
        else:
            mock.return_value = response

    def mock_find_config_environment(self, response):
        mock = patch(
            'networkapi.ambiente.models.ConfigEnvironment.get_by_environment').start()
        mock.return_value = Mock()
        mock.return_value.filter.return_value = response

    def mock_get_networks(self, response):
        mock = patch('networkapi.ip.models.NetworkIPv4.objects.filter').start()
        mock.return_value = response

    def mock_save_network(self):
        return patch('networkapi.ip.models.NetworkIPv4.save').start()

    def mock_distributed_lock(self):
        patch('networkapi.ip.models.distributedlock').start()

    def mock_transaction(self):
        patch('networkapi.ip.models.transaction').start()
