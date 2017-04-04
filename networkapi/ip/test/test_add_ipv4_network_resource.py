# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from django.test import Client
from mock import patch

from networkapi.ambiente.models import ConfigEnvironmentInvalidError
from networkapi.ambiente.models import EnvironmentVip
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import NetworkIPv4AddressNotAvailableError
from networkapi.test import mock_login
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import VlanNotFoundError

XML = """
<networkapi>
    <vlan>
        <id_vlan>{vlan}</id_vlan>
        <id_tipo_rede>{net_type}</id_tipo_rede>
        <id_ambiente_vip>{vip_env}</id_ambiente_vip>
        <prefix>{cidr}</prefix>
    </vlan>
</networkapi>
"""


class NetworkAddTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.mock_user_has_permission(True)

    def tearDown(self):
        patch.stopall()

    @mock_login
    def test_add_network_given_user_without_permission(self):
        self.mock_user_has_permission(False)

        response = self.client.post(
            '/network/ipv4/add/', '', content_type='text/xml')
        self.assertEquals(
            '402 - Usuário não autorizado para executar a operação.', response.content)
        self.assertEquals(402, response.status_code)

    @mock_login
    def test_add_network_given_xml_without_vlan_xml_node(self):
        response = self.client.post(
            '/network/ipv4/add/', '<networkapi></networkapi>', content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Falha ao executar a leitura do XML de requisição. Causa: There is no value to the networkapi tag of XML request.',
                          xml_map.get('networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_invalid_cidr(self):
        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='a', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Parameter prefix is invalid. Value: a', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_invalid_cidr_greater_than_33(self):
        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='33', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Parameter prefix is invalid. Value: 33', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_invalid_vlan_id(self):
        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan='a', vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Parameter id_vlan is invalid. Value: a', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_invalid_network_type(self):
        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type='a'), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Parameter id_tipo_rede is invalid. Value: a', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_invalid_network_type_not_found(self):
        self.mock_get_network_type_by_pk(NetworkTypeNotFoundError(''))

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Type of network not registered', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_invalid_vip_environment_id(self):
        self.mock_get_network_type_by_pk(TipoRede(id=1))

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env='a', net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Parameter id_ambiente_vip is invalid. Value: a', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_vip_environment_not_found(self):
        self.mock_get_network_type_by_pk(TipoRede(id=1))
        self.mock_get_vip_environment_by_pk(EnvironmentVipNotFoundError(''))

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Environment VIP not registered', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_add_network_given_vlan_not_found(self):
        self.mock_get_network_type_by_pk(TipoRede(id=1))
        self.mock_get_vip_environment_by_pk(EnvironmentVip(id=1))
        add_network_mock = self.mock_add_network_ipv4(VlanNotFoundError(''))

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('VLAN not registered', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)
        self.assertTrue(add_network_mock.called)

    @mock_login
    def test_add_network_given_invalid_environment_config(self):
        self.mock_get_network_type_by_pk(TipoRede(id=1))
        self.mock_get_vip_environment_by_pk(EnvironmentVip(id=1))
        add_network_mock = self.mock_add_network_ipv4(
            ConfigEnvironmentInvalidError(''))

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Invalid Environment Configuration or not registered', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)
        self.assertTrue(add_network_mock.called)

    @mock_login
    def test_add_network_given_no_more_available_ip_addresses(self):
        self.mock_get_network_type_by_pk(TipoRede(id=1))
        self.mock_get_vip_environment_by_pk(EnvironmentVip(id=1))
        add_network_mock = self.mock_add_network_ipv4(
            NetworkIPv4AddressNotAvailableError(''))

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Unavailable address to create a NetworkIPv4', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)
        self.assertTrue(add_network_mock.called)

    @mock_login
    def test_add_network_given_no_first_ip_available(self):
        self.mock_get_network_type_by_pk(TipoRede(id=1))
        self.mock_get_vip_environment_by_pk(EnvironmentVip(id=1))
        add_network_mock = self.mock_add_network_ipv4({'vlan': {}})
        self.mock_get_equipamento_ambiente(
            EquipamentoAmbiente(equipamento=Equipamento(id=1)))
        self.mock_get_first_available_ip(
            IpNotAvailableError('Endereço IP não dispoínvel'))

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Causa: Endereço IP não dispoínvel, Mensagem: None', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)
        self.assertTrue(add_network_mock.called)

    @mock_login
    def test_add_network_given_successfully(self):
        self.mock_get_network_type_by_pk(TipoRede(id=1))
        self.mock_get_vip_environment_by_pk(EnvironmentVip(id=1))
        add_network_mock = self.mock_add_network_ipv4(self.get_vlan_map())
        self.mock_get_equipamento_ambiente(
            EquipamentoAmbiente(equipamento=Equipamento(id=1)))
        self.mock_get_first_available_ip('192.168.10.18')
        self.mock_ip_save()
        self.mock_ip_equipamento_create()

        response = self.client.post('/network/ipv4/add/', XML.format(
            cidr='24', vlan=1, vip_env=1, net_type=1), content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertIsNotNone(xml_map.get('networkapi').get('vlan'))
        self.assertEquals(200, response.status_code)
        self.assertTrue(add_network_mock.called)

    # MOCKS
    def mock_user_has_permission(self, has_permission):
        permission_decorator = patch(
            'networkapi.ip.resource.NetworkIPv4AddResource.has_perm').start()
        permission_decorator.return_value = has_permission

    def mock_get_network_type_by_pk(self, response):
        mock = patch('networkapi.vlan.models.TipoRede.get_by_pk').start()
        if issubclass(response.__class__, Exception):
            mock.side_effect = response
        else:
            mock.return_value = response

    def mock_get_vip_environment_by_pk(self, response):
        mock = patch(
            'networkapi.ambiente.models.EnvironmentVip.get_by_pk').start()
        if issubclass(response.__class__, Exception):
            mock.side_effect = response
        else:
            mock.return_value = response

    def mock_add_network_ipv4(self, response):
        mock = patch(
            'networkapi.ip.models.NetworkIPv4.add_network_ipv4').start()
        if issubclass(response.__class__, Exception):
            mock.side_effect = response
        else:
            mock.return_value = response
        return mock

    def mock_get_equipamento_ambiente(self, response):
        patch('networkapi.ip.models.NetworkIPv4.vlan').start()
        mock = patch(
            'networkapi.equipamento.models.EquipamentoAmbiente.get_routers_by_environment').start()
        mock.return_value = [response]
        return mock

    def mock_get_first_available_ip(self, response):
        mock = patch('networkapi.ip.models.Ip.get_first_available_ip').start()
        if issubclass(response.__class__, Exception):
            mock.side_effect = response
        else:
            mock.return_value = response
        return mock

    def mock_ip_save(self):
        patch('networkapi.ip.models.Ip.save').start()

    def mock_ip_equipamento_create(self):
        patch('networkapi.ip.models.IpEquipamento.create').start()

    def get_vlan_map(self):
        vlan_map = dict()
        vlan_map['id'] = 1
        vlan_map['nome'] = 'vlan'
        vlan_map['num_vlan'] = '1'
        vlan_map['id_tipo_rede'] = 1
        vlan_map['id_ambiente'] = 1
        vlan_map['rede_oct1'] = 192
        vlan_map['rede_oct2'] = 168
        vlan_map['rede_oct3'] = 10
        vlan_map['rede_oct4'] = 0
        vlan_map['bloco'] = 24
        vlan_map['mascara_oct1'] = 255
        vlan_map['mascara_oct2'] = 255
        vlan_map['mascara_oct3'] = 255
        vlan_map['mascara_oct4'] = 255
        vlan_map['broadcast'] = ''
        vlan_map['descricao'] = 'desc'
        vlan_map['acl_file_name'] = 'file_name'
        vlan_map['acl_valida'] = 0
        vlan_map['acl_file_name_v6'] = 'file_name_v6'
        vlan_map['acl_valida_v6'] = 0
        vlan_map['ativada'] = 0
        vlan_map['id_network'] = 1

        return {
            'vlan': vlan_map
        }

    def parse_response(self, response):
        return loads(response.content)[0]
