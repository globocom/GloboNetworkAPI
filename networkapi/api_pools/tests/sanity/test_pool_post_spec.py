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


class PoolPostSpecTestCase(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def execute_some_post_verify_error(self, name_file):

        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

    def execute_some_post_verify_success(self, name_file):

        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_pool = response.data[0]['id']

        # get data inserted
        response = self.client.get(
            '/api/v3/pool/%s/' % id_pool,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = response.data
        del data['server_pools'][0]['id']

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, data)

    def test_post_valid_file(self):
        """ test_post_valid_file"""
        self.execute_some_post_verify_success(
            'api_pools/tests/sanity/json/post/test_pool_post_valid_file.json')

    def test_post_out_of_range_port(self):
        """ test_post_out_of_range_port"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_out_of_range_port.json')

    def test_post_negative_port(self):
        """ test_post_negative_port"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_negative_port.json')

    def test_post_float_port(self):
        """ test_post_float_port"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_float_port.json')

    def test_post_zero_port(self):
        """ test_post_zero_port"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_zero_port.json')

    def test_post_string_port(self):
        """ test_post_string_port"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_string_port.json')

    def test_post_float_environment(self):
        """ test_post_float_environment"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_float_environment.json')

    def test_post_string_environment(self):
        """ test_post_string_environment"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_string_environment.json')

    def test_post_zero_environment(self):
        """ test_post_zero_environment"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_zero_environment.json')

    def test_post_negative_environment(self):
        """ test_post_negative_environment"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_negative_environment.json')

    def test_post_integer_name_servicedownaction(self):
        """ test_post_integer_name_servicedownaction"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_integer_name_servicedownaction.json')

    def test_post_invalid_healthcheck_type(self):
        """ test_post_invalid_healthcheck_type"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_invalid_healthcheck_type.json')

    def test_post_invalid_destination(self):
        """ test_post_invalid_destination"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_invalid_destination.json')

    def test_post_negative_default_limit(self):
        """ test_post_negative_default_limit"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_negative_default_limit.json')

    def test_post_integer_lb_method(self):
        """ test_post_integer_lb_method"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_integer_lb_method.json')

    def test_post_string_id_servicedownaction(self):
        """  test_post_string_id_servicedownaction"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_string_id_servicedownaction.json')

    def test_post_zero_id_servicedownaction(self):
        """  test_post_zero_id_servicedownaction"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_zero_id_servicedownaction.json')

    def test_post_negative_id_servicedownaction(self):
        """  test_post_negative_id_servicedownaction"""
        self.execute_some_post_verify_error(
            'api_pools/tests/sanity/json/post/test_pool_post_negative_id_servicedownaction.json')
