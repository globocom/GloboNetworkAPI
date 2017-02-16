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
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        verbosity=0
    )


class EnvironmentPutTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_one_env_success(self):
        """Test of success for put one environment."""

        name_file = 'api_environment/tests/sanity/json/put_one_env.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property name
        data = response.data
        del data['environments'][0]['name']

        self.compare_json(name_file, data)

    def test_put_two_env_success(self):
        """Test of success for put two environments."""

        name_file = 'api_environment/tests/sanity/json/put_two_env.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/1;2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property name in each dict
        data = response.data
        del data['environments'][0]['name']
        del data['environments'][1]['name']

    def test_put_one_env_duplicate_error(self):
        """Test of error for put one duplicated environment."""

        name_file = 'api_environment/tests/sanity/json/put_one_env_duplicate_error.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)
