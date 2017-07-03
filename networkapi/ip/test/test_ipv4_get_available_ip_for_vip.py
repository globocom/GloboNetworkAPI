# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from django.test import Client
from mock import Mock
from mock import patch

from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import TipoEquipamento
from networkapi.infrastructure.ipaddr import IPv4Address
from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import NetworkIPv4
from networkapi.test import mock_login

XML = """
<networkapi>
    <ip_map>
        <id_evip>%s</id_evip>
        <name>name</name>
    </ip_map>
</networkapi>
"""


class CreateVipTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        patch.stopall()

    @mock_login
    def test_check_available_ip_given_user_withou_permission(self):
        self.mock_user_has_permission(False)

        response = self.client.post(
            '/ip/availableip4/vip/1/', XML, content_type='text/xml')
        self.assertEquals(
            '402 - Usuário não autorizado para executar a operação.', response.content)
        self.assertEquals(402, response.status_code)

    @mock_login
    def test_check_available_ip_given_invalid_vip_environment_id(self):
        self.mock_user_has_permission(True)

        response = self.client.post(
            '/ip/availableip4/vip/1/', XML % 'a', content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Parameter id_evip is invalid. Value: a', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_check_available_ip_given_vip_environment_without_networks(self):
        self.mock_user_has_permission(True)
        self.mock_get_vip_environment_by_pk(
            self.mock_vip_environment(1, 'production env', networks=[]))

        response = self.client.post(
            '/ip/availableip4/vip/1/', XML % 1, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Não há rede ipv4 no ambiente vip fornecido.', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_check_available_ip_given_no_ip_available_on_network(self):
        self.mock_user_has_permission(True)
        self.mock_get_vip_environment_by_pk(
            self.mock_vip_environment(1, 'prod', networks=[NetworkIPv4()]))
        self.mock_network_get_available_ip(IpNotAvailableError(None, ''))

        response = self.client.post(
            '/ip/availableip4/vip/1/', XML % 1, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Não há ipv4 disponivel para as redes associdas com o Ambiente Vip: prod - prod - prod',
                          xml_map.get('networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_check_available_ip_given_no_load_balancer_equipment_available_on_network(self):
        ip_equipamento = IpEquipamento(equipamento=Equipamento(
            tipo_equipamento=TipoEquipamento(id=2, tipo_equipamento='router')))
        network = self.mock_network(ip_equipamento)

        self.mock_user_has_permission(True)
        self.mock_get_vip_environment_by_pk(
            self.mock_vip_environment(1, 'production env', networks=[network]))
        self.mock_network_get_available_ip(IPv4Address('192.168.1.1'))
        self.mock_get_tipo_balanceador(TipoEquipamento(
            id=1, tipo_equipamento='balanceador'))

        response = self.client.post(
            '/ip/availableip4/vip/1/', XML % 1, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Não há ipv4 disponivel para as redes associdas com o Ambiente '
                          'Vip: production env - production env - production env, pois não existe '
                          'equipamentos do Tipo Balanceador nessas redes.', xml_map.get('networkapi').get('erro').get('descricao'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_check_available_ip(self):
        ip_equipamento = IpEquipamento(equipamento=Equipamento(
            tipo_equipamento=TipoEquipamento(id=1, tipo_equipamento='balanceador')))
        network = self.mock_network(ip_equipamento)

        self.mock_user_has_permission(True)
        self.mock_get_vip_environment_by_pk(
            self.mock_vip_environment(1, 'production env', networks=[network]))
        self.mock_network_get_available_ip(IPv4Address('192.168.1.1'))
        self.mock_get_tipo_balanceador(TipoEquipamento(
            id=1, tipo_equipamento='balanceador'))
        ip_save_mock = self.mock_ip_save()

        response = self.client.post(
            '/ip/availableip4/vip/1/', XML % 1, content_type='text/xml')

        print(response)
        xml_map = self.parse_response(response)
        self.assertEquals('192', xml_map.get(
            'networkapi').get('ip').get('oct1'))
        self.assertEquals('168', xml_map.get(
            'networkapi').get('ip').get('oct2'))
        self.assertEquals('1', xml_map.get('networkapi').get('ip').get('oct3'))
        self.assertEquals('1', xml_map.get('networkapi').get('ip').get('oct4'))
        self.assertEquals(200, response.status_code)
        self.assertTrue(ip_save_mock.called)

    def mock_network(self, equip_environment):
        network = Mock(vlan=Mock(ambiente=Mock()))
        network.vlan.ambiente.equipamentoambiente_set.all = lambda: [
            equip_environment]
        return network

    # MOCKS
    def mock_vip_environment(self, id, desc, networks):
        mock = Mock(id=id, description=desc, finalidade_txt=desc,
                    ambiente_p44_txt=desc, cliente_txt=desc)
        mock.networkipv4_set = Mock(all=lambda: networks)
        return mock

    def mock_user_has_permission(self, has_permission):
        permission_decorator = patch(
            'networkapi.ip.resource.Ipv4GetAvailableForVipResource.has_perm').start()
        permission_decorator.return_value = has_permission

    def mock_get_vip_environment_by_pk(self, response):
        mock = patch(
            'networkapi.ambiente.models.EnvironmentVip.get_by_pk').start()
        mock.return_value = response

    def mock_network_get_available_ip(self, response):
        mock = patch('networkapi.ip.models.Ip.get_available_ip').start()
        if issubclass(response.__class__, Exception):
            mock.side_effect = response
        else:
            mock.return_value = response

    def mock_get_tipo_balanceador(self, response):
        mock = patch(
            'networkapi.equipamento.models.TipoEquipamento.get_tipo_balanceador').start()
        mock.return_value = response

    def mock_ip_save(self):
        return patch('networkapi.ip.models.Ip.save_ipv4').start()

    # UTILS
    def parse_response(self, response):
        return loads(response.content)[0]
