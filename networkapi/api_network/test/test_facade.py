# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
import logging
from mock import patch, MagicMock
from networkapi.ambiente.models import Ambiente
from networkapi.api_network.exceptions import IncorrectRedundantGatewayRegistryException
from networkapi.api_network.facade import deploy_networkIPv4_configuration, deploy_networkIPv6_configuration
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.ip.models import NetworkIPv4, NetworkIPv6, Ip, Ipv6, IpEquipamento, Ipv6Equipament
from networkapi.roteiro.models import Roteiro
from networkapi.usuario.models import Usuario
from networkapi.vlan.models import Vlan

LOG = logging.getLogger(__name__)

class NetworkFacadeTestCase(unittest.TestCase):

    def setUp(self):
        self.user = Usuario()
        self.equipment_list = [Equipamento(id = 1, nome = 'router')]
        self.ambiente = Ambiente()
        self.vlan = Vlan(id=1, ambiente=self.ambiente)
        self.networkv4 = NetworkIPv4(id = 1, vlan = self.vlan, oct1 = 192, oct2 = 168, oct3 = 0, oct4 = 0,
                                     mask_oct1 = 255, mask_oct2 = 255, mask_oct3 = 255, mask_oct4 = 0)

        self.networkv6 = NetworkIPv6(id = 1, vlan = self.vlan, block1 = 'fff', block2 = 'fff', block3 = 'fff',
                                    block4 = 'fff', block5 = 'fff', block6 = 'fff', block7 = 'fff', block8 = 'fff',
                                    mask1 = 'fff', mask2 = 'fff', mask3 = 'fff', mask4 = 'fff',
                                    mask5 = 'fff', mask6 = 'fff', mask7 = 'fff', mask8 = 'fff')

        self.mock_distributed_lock()
        self.mock_transaction()

    def tearDown(self):
        pass

    def test_deploy_networkIPv4_configuration_given_network_already_active(self):
        self.networkv4.active = True

        response = deploy_networkIPv4_configuration(self.user, self.networkv4, self.equipment_list)
        self.assertEqual('Network already active. Nothing to do.', response['output'], "Nothing to be done.No actions should me taken")

    def test_deploy_networkIPv4_configuration_given_gateway_ip_not_found(self):
        self.mock_ip_get_by_octets(None)

        with self.assertRaises(IncorrectRedundantGatewayRegistryException):
            deploy_networkIPv4_configuration(self.user, self.networkv4, self.equipment_list)

    def test_deploy_networkIPv4_configuration_given_gateway_equipment_not_found(self):
        self.mock_ip_get_by_octets(Ip(oct1 = 192, oct2 = 168, oct3 = 0, oct4 = 0))
        self.mock_find_equipamento_ip([])

        with self.assertRaises(IncorrectRedundantGatewayRegistryException):
            deploy_networkIPv4_configuration(self.user, self.networkv4, self.equipment_list)

    def test_deploy_networkIPv4_configuration_with_active_vlan(self):
        self.networkv4.vlan.ativada = True

        self.mock_ip_get_by_octets(Ip(oct1 = 192, oct2 = 168, oct3 = 0, oct4 = 0))
        self.mock_find_equipamento_ip([IpEquipamento()])
        self.mock_find_roteiro(EquipamentoRoteiro(roteiro = Roteiro(roteiro = 'roteiro')))
        self.mock_template_file_read('script content')
        deploy_config_mock = self.mock_deploy_config('config_deployed')
        network_activation_mock = self.mock_network_activation()
        vlan_activation_mock = self.mock_vlan_activation()

        response = deploy_networkIPv4_configuration(self.user, self.networkv4, self.equipment_list)

        self.assertTrue(deploy_config_mock.called)
        network_activation_mock.assert_called_with(self.user)
        self.assertFalse(vlan_activation_mock.called)
        self.assertEquals({1: 'config_deployed'}, response)

    def test_deploy_networkIPv4_configuration_with_inactive_vlan(self):
        self.networkv4.vlan.ativada = False

        self.mock_ip_get_by_octets(Ip(oct1 = 192, oct2 = 168, oct3 = 0, oct4 = 0))
        self.mock_find_equipamento_ip([IpEquipamento()])
        self.mock_find_roteiro(EquipamentoRoteiro(roteiro = Roteiro(roteiro = 'roteiro')))
        self.mock_template_file_read('script content')
        deploy_config_mock = self.mock_deploy_config('config_deployed')
        network_activation_mock = self.mock_network_activation()
        vlan_activation_mock = self.mock_vlan_activation()

        response = deploy_networkIPv4_configuration(self.user, self.networkv4, self.equipment_list)

        self.assertTrue(deploy_config_mock.called)
        network_activation_mock.assert_called_with(self.user)
        vlan_activation_mock.assert_called_with(self.user)
        self.assertEquals({1: 'config_deployed'}, response)

    def test_deploy_networkIPv6_configuration_given_network_already_active(self):
        self.networkv6.active = True

        response = deploy_networkIPv6_configuration(self.user, self.networkv6, self.equipment_list)
        self.assertEqual('Network already active. Nothing to do.', response['output'], "Nothing to be done.No actions should me taken")

    def test_deploy_networkIPv6_configuration_given_gateway_ip_not_found(self):
        self.mock_ip_get_by_blocks_and_net(None)

        with self.assertRaises(IncorrectRedundantGatewayRegistryException):
            deploy_networkIPv6_configuration(self.user, self.networkv6, self.equipment_list)

    def test_deploy_networkIPv6_configuration_given_gateway_equipment_not_found(self):
        self.mock_ip_get_by_blocks_and_net(Ipv6(block1 = 'fff', block2 = 'fff', block3 = 'fff', block4 = 'fff',
                                                block5 = 'fff', block6 = 'fff', block7 = 'fff', block8 = 'fff'))
        self.mock_find_equipamento_ipv6([])

        with self.assertRaises(IncorrectRedundantGatewayRegistryException):
            deploy_networkIPv6_configuration(self.user, self.networkv6, self.equipment_list)

    def test_deploy_networkIPv6_configuration_with_active_vlan(self):
        self.networkv6.vlan.ativada = True

        self.mock_ip_get_by_blocks_and_net(Ipv6(block1 = 'fff', block2 = 'fff', block3 = 'fff', block4 = 'fff',
                                                block5 = 'fff', block6 = 'fff', block7 = 'fff', block8 = 'fff'))
        self.mock_find_equipamento_ipv6([Ipv6Equipament()])
        self.mock_find_roteiro(EquipamentoRoteiro(roteiro = Roteiro(roteiro = 'roteiro')))
        self.mock_template_file_read('script content')
        deploy_config_mock = self.mock_deploy_config('config_deployed')
        network_activation_mock = self.mock_networkv6_activation()
        vlan_activation_mock = self.mock_vlan_activation()

        response = deploy_networkIPv6_configuration(self.user, self.networkv6, self.equipment_list)

        self.assertTrue(deploy_config_mock.called)
        network_activation_mock.assert_called_with(self.user)
        self.assertFalse(vlan_activation_mock.called)
        self.assertEquals({1: 'config_deployed'}, response)

    def test_deploy_networkIPv6_configuration_with_inactive_vlan(self):
        self.networkv6.vlan.ativada = False

        self.mock_ip_get_by_blocks_and_net(Ipv6(block1 = 'fff', block2 = 'fff', block3 = 'fff', block4 = 'fff',
                                                block5 = 'fff', block6 = 'fff', block7 = 'fff', block8 = 'fff'))
        self.mock_find_equipamento_ipv6([Ipv6Equipament()])
        self.mock_find_roteiro(EquipamentoRoteiro(roteiro = Roteiro(roteiro = 'roteiro')))
        self.mock_template_file_read('script content')
        deploy_config_mock = self.mock_deploy_config('config_deployed')
        network_activation_mock = self.mock_networkv6_activation()
        vlan_activation_mock = self.mock_vlan_activation()

        response = deploy_networkIPv6_configuration(self.user, self.networkv6, self.equipment_list)

        self.assertTrue(deploy_config_mock.called)
        network_activation_mock.assert_called_with(self.user)
        vlan_activation_mock.assert_called_with(self.user)
        self.assertEquals({1: 'config_deployed'}, response)

    #MOCKS
    def mock_distributed_lock(self):
        patch('networkapi.api_network.facade.distributedlock').start()
        patch('networkapi.api_deploy.facade.distributedlock').start()

    def mock_ip_get_by_octets(self, ip):
        get_by_octs_and_net_mock = patch('networkapi.ip.models.Ip.get_by_octs_and_net').start()
        get_by_octs_and_net_mock.return_value = ip

    def mock_ip_get_by_blocks_and_net(self, ipv6):
        get_by_octs_and_net_mock = patch('networkapi.ip.models.Ipv6.get_by_blocks_and_net').start()
        get_by_octs_and_net_mock.return_value = ipv6

    def mock_find_equipamento_ip(self, ip_equipamento_list):
        find_ip_equipamento_mock = patch('networkapi.ip.models.IpEquipamento.objects.filter').start()
        find_ip_equipamento_mock.return_value = ip_equipamento_list

    def mock_find_equipamento_ipv6(self, ip_equipamento_list):
        find_ip_equipamento_mock = patch('networkapi.ip.models.Ipv6Equipament.objects.filter').start()
        find_ip_equipamento_mock.return_value = ip_equipamento_list

    def mock_find_roteiro(self, equip_roteiro):
        find_equip_roteiro_mock = patch('networkapi.equipamento.models.EquipamentoRoteiro.search').start()
        equip_roteiro_list = MagicMock()
        equip_roteiro_list.uniqueResult.return_value = equip_roteiro
        find_equip_roteiro_mock.return_value = equip_roteiro_list

    def mock_template_file_read(self, template_content):
        open_mock = patch('networkapi.api_network.facade.open', create=True).start()
        file_handle = MagicMock()
        file_handle.read.return_value = template_content
        open_mock.return_value = file_handle

    def mock_deploy_config(self, response):
        deploy_config_mock = patch('networkapi.api_network.facade.deploy_config_in_equipment_synchronous').start()
        deploy_config_mock.return_value = response
        return deploy_config_mock

    def mock_network_activation(self):
        self.networkv4.activate = MagicMock()
        return self.networkv4.activate

    def mock_networkv6_activation(self):
        self.networkv6.activate = MagicMock()
        return self.networkv6.activate

    def mock_vlan_activation(self):
        return patch('networkapi.vlan.models.Vlan.activate').start()

    def mock_transaction(self):
        patch('networkapi.api_network.facade.transaction').start()