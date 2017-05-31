# -*- coding: utf-8 -*-
import logging

from django.core.management import call_command
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
log = logging.getLogger(__name__)


def setup():
    call_command(
        'loaddata',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/api_pools/fixtures/initial_optionspool.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/healthcheckexpect/fixtures/initial_healthcheck.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_vip_request/fixtures/initial_base_environment.json',
        'networkapi/api_vip_request/fixtures/initial_base_pool.json',
        'networkapi/api_vip_request/fixtures/initial_vip_request.json',
        verbosity=0
    )


class VipRequestGetTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_one_vip_success(self):
        """
        Test Success of one vip request
        """
        response = self.client.get(
            '/api/v3/vip-request/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    def test_get_two_vip_success(self):
        """
        Test Success of two vips request
        """
        call_command(
            'loaddata', 'networkapi/api_vip_request/fixtures/initial_base_pool.json', verbosity=0)

        response = self.client.get(
            '/api/v3/vip-request/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    def test_get_list_vip_success(self):
        """
        Test Success of vip request list
        """
        response = self.client.get(
            '/api/v3/vip-request/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    def test_get_one_vip_details_success(self):
        """
        Test Success of one vip request(details)
        """
        response = self.client.get(
            '/api/v3/vip-request/details/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    def test_get_two_vip_details_success(self):
        """
        Test Success of two vips request(details)
        """
        response = self.client.get(
            '/api/v3/vip-request/details/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    def test_get_list_vip_details_success(self):
        """
        Test Success of vip request list(details)
        """
        response = self.client.get(
            '/api/v3/vip-request/details/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    def test_get_list_vip_by_pool_success(self):
        """
        Test Success of request by pool
        """
        response = self.client.get(
            '/api/v3/vip-request/pool/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)
