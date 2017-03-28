# -*- coding: utf-8 -*-
import json
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
        'networkapi/api_pools/fixtures/initial_base.json',
        'networkapi/api_pools/fixtures/initial_pools_1.json',
        verbosity=0
    )


class PoolPutSpecTestCase(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def execute_some_put_verify_error(self, name_file):
        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

    def execute_some_put_verify_success(self, name_file):
        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # get datas updated
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_put_valid_file(self):
        """ test_put_valid_file"""
        self.execute_some_put_verify_success(
            'api_pools/tests/sanity/json/put/test_pool_put_valid_file.json')

    def test_put_out_of_range_port(self):
        """ test_put_out_of_range_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_out_of_range_port.json')

    def test_put_negative_port(self):
        """ test_put_negative_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_negative_port.json')

    def test_put_float_port(self):
        """ test_put_float_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_float_port.json')

    def test_put_zero_port(self):
        """ test_put_zero_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_zero_port.json')

    def test_put_string_port(self):
        """ test_put_string_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_string_port.json')

    def test_put_float_environment(self):
        """ test_put_float_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_float_environment.json')

    def test_put_string_environment(self):
        """ test_put_string_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_string_environment.json')

    def test_put_zero_environment(self):
        """ test_put_zero_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_zero_environment.json')

    def test_put_negative_environment(self):
        """ test_put_negative_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_negative_environment.json')

    def test_put_integer_name_servicedownaction(self):
        """ test_put_integer_name_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_integer_name_servicedownaction.json')

    def test_put_invalid_healthcheck_type(self):
        """ test_put_invalid_healthcheck_type"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_invalid_healthcheck_type.json')

    def test_put_invalid_destination(self):
        """ test_put_invalid_destination"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_invalid_destination.json')

    def test_put_negative_default_limit(self):
        """ test_put_negative_default_limit"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_negative_default_limit.json')

    def test_put_integer_lb_method(self):
        """ test_put_integer_lb_method"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_integer_lb_method.json')

    def test_put_string_id_servicedownaction(self):
        """  test_put_string_id_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_string_id_servicedownaction.json')

    def test_put_zero_id_servicedownaction(self):
        """  test_put_zero_id_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_zero_id_servicedownaction.json')

    def test_put_negative_id_servicedownaction(self):
        """  test_put_negative_id_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/sanity/json/put/test_pool_put_negative_id_servicedownaction.json')

    def test_valid_post_after_equals_valid_put(self):
        """ test_valid_post_after_equals_valid_put"""

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file(
                'api_pools/tests/sanity/json/test_pool_put_and_post.json')),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(
                'api_pools/tests/sanity/json/test_pool_put_and_post.json')),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(400, response.status_code,
                         'Status code should be 500 and was %s' % response.status_code)
