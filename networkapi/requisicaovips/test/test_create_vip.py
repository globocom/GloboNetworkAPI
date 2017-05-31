# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from django.db.models.loading import cache as model_cache
from django.test import Client
from mock import patch

from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import Ip
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import ServerPool
from networkapi.settings import VIP_CREATE
from networkapi.test import mock_login

VIP_XML = """
<networkapi>
    <vip>
        <id_vip>1</id_vip>
    </vip>
</networkapi>
"""


class CreateVipTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.mock_distributed_lock()

        # workaround on model loading issue
        # http://stackoverflow.com/questions/14386536/instantiating-django-model-raises-typeerror-isinstance-arg-2-must-be-a-class
        if not model_cache.loaded:
            model_cache._populate()

        self.ip = Ip(oct1=192, oct2=168, oct3=0, oct4=15)
        self.vip = RequisicaoVips(id=1, ip=self.ip)

    def tearDown(self):
        patch.stopall()

    @mock_login
    def test_create_vip_given_user_without_permission(self):
        self.mock_user_has_permission(False)
        response = self.client.post(
            '/vip/create/', VIP_XML, content_type='text/xml')
        self.assertEquals(
            '402 - Usuário não autorizado para executar a operação.', response.content)
        self.assertEquals(402, response.status_code)

    @mock_login
    def test_create_vip_given_xml_without_networkapi_node(self):
        self.mock_user_has_permission(True)
        response = self.client.post(
            '/vip/create/', '<vip></vip>', content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Falha ao executar a leitura do XML de requisição. Causa: There is no value to the networkapi tag of XML request.', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals('0003', xml_map.get(
            'networkapi').get('erro').get('codigo'))
        self.assertTrue(
            'There is no value to the networkapi tag of XML request.' in response.content)
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_create_vip_given_xml_without_vip_node(self):
        self.mock_user_has_permission(True)
        response = self.client.post(
            '/vip/create/', '<networkapi><something></something></networkapi>', content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Falha ao executar a leitura do XML de requisição. Causa: There is no value to the vip tag of XML request.', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals('0003', xml_map.get(
            'networkapi').get('erro').get('codigo'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_create_vip_given_xml_without_vip_id(self):
        self.mock_user_has_permission(True)
        response = self.client.post(
            '/vip/create/', '<networkapi><vip><id_vip></id_vip></vip></networkapi>', content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Parameter id_vip is invalid. Value: None', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals('0269', xml_map.get(
            'networkapi').get('erro').get('codigo'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_create_vip_given_vip_not_validated(self):
        self.vip.validado = False
        self.mock_user_has_permission(True)
        self.mock_requisicao_vip_get_by_pk(self.vip)
        response = self.client.post(
            '/vip/create/', VIP_XML, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Requisição de VIP 1 não validada', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals('0191', xml_map.get(
            'networkapi').get('erro').get('codigo'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_create_vip_given_vip_already_created(self):
        self.vip.validado = True
        self.vip.vip_criado = True
        self.mock_user_has_permission(True)
        self.mock_requisicao_vip_get_by_pk(self.vip)
        response = self.client.post(
            '/vip/create/', VIP_XML, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Requisição de VIP 1 já criada', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals('0192', xml_map.get(
            'networkapi').get('erro').get('codigo'))
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_create_vip_given_script_error(self):
        self.vip.validado = True
        self.vip.vip_criado = False
        self.mock_user_has_permission(True)
        self.mock_requisicao_vip_get_by_pk(self.vip)
        exec_script_mock = self.mock_exec_script((1, '', ' invalid vip'))

        response = self.client.post(
            '/vip/create/', VIP_XML, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('Falha ao executar o script. Causa:  invalid vip', xml_map.get(
            'networkapi').get('erro').get('descricao'))
        self.assertEquals('0002', xml_map.get(
            'networkapi').get('erro').get('codigo'))
        exec_script_mock.assert_called_with(VIP_CREATE % 1)
        self.assertEquals(500, response.status_code)

    @mock_login
    def test_create_vip_successfully(self):
        self.vip.validado = True
        self.vip.vip_criado = False
        self.mock_user_has_permission(True)
        self.mock_requisicao_vip_get_by_pk(self.vip)
        exec_script_mock = self.mock_exec_script(
            (0, 'load balancer output', ''))
        vip_save_mock = self.mock_vip_save()
        self.mock_find_pools([])

        response = self.client.post(
            '/vip/create/', VIP_XML, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('load balancer output', xml_map.get(
            'networkapi').get('sucesso').get('descricao').get('stdout'))
        self.assertEquals('0000', xml_map.get(
            'networkapi').get('sucesso').get('codigo'))
        self.assertEquals(200, response.status_code)
        self.assertTrue(self.vip.vip_criado)
        self.assertTrue(vip_save_mock.called)
        exec_script_mock.assert_called_with(VIP_CREATE % 1)

    @mock_login
    def test_create_vip_with_pools(self):
        server_pools = [ServerPool(id=1), ServerPool(id=2)]

        self.vip.validado = True
        self.vip.vip_criado = False
        self.mock_user_has_permission(True)
        self.mock_requisicao_vip_get_by_pk(self.vip)
        exec_script_mock = self.mock_exec_script(
            (0, 'load balancer output', ''))
        vip_save_mock = self.mock_vip_save()
        find_pools_mock = self.mock_find_pools(server_pools)
        pool_save_mock = self.mock_pool_save()

        response = self.client.post(
            '/vip/create/', VIP_XML, content_type='text/xml')

        xml_map = self.parse_response(response)
        self.assertEquals('load balancer output', xml_map.get(
            'networkapi').get('sucesso').get('descricao').get('stdout'))
        self.assertEquals('0000', xml_map.get(
            'networkapi').get('sucesso').get('codigo'))
        self.assertEquals(200, response.status_code)
        exec_script_mock.assert_called_with(VIP_CREATE % 1)
        self.assertTrue(vip_save_mock.called)
        self.assertTrue(find_pools_mock.called)
        self.assertTrue(pool_save_mock.called)
        self.assertTrue(server_pools[0].pool_created)
        self.assertTrue(server_pools[1].pool_created)
        self.assertTrue(self.vip.vip_criado)

    def mock_user_has_permission(self, has_permission):
        permission_decorator = patch(
            'networkapi.requisicaovips.resource.CreateVipResource.has_perm').start()
        permission_decorator.return_value = has_permission

    def mock_distributed_lock(self):
        patch(
            'networkapi.requisicaovips.resource.CreateVipResource.distributedlock').start()

    def mock_requisicao_vip_get_by_pk(self, vip):
        get_by_pk_mock = patch(
            'networkapi.requisicaovips.models.RequisicaoVips.get_by_pk').start()
        get_by_pk_mock.return_value = vip

    def mock_exec_script(self, script_output):
        exec_script_mock = patch(
            'networkapi.requisicaovips.resource.CreateVipResource.exec_script').start()
        exec_script_mock.return_value = script_output
        return exec_script_mock

    def mock_vip_save(self):
        return patch('networkapi.requisicaovips.models.RequisicaoVips.save').start()

    def mock_pool_save(self):
        return patch('networkapi.requisicaovips.models.ServerPool.save').start()

    def mock_find_pools(self, pools):
        find_pools_mock = patch(
            'networkapi.requisicaovips.models.ServerPool.objects.filter').start()
        find_pools_mock.return_value = pools
        return find_pools_mock

    def parse_response(self, response):
        return loads(response.content)[0]
