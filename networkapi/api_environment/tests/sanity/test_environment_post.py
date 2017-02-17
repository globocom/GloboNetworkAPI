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


class EnvironmentPostTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_env_success(self):
        """Test of success for post one environment."""

        name_file = 'api_environment/tests/sanity/json/post_one_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/environment/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id/name
        data = response.data
        del data['environments'][0]['id']
        del data['environments'][0]['name']

        self.compare_json(name_file, data)

    def test_post_two_env_success(self):
        """Test of success for post two environment."""

        name_file = 'api_environment/tests/sanity/json/post_two_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env_one = response.data[0]['id']
        id_env_two = response.data[1]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/environment/%s;%s/' % (id_env_one, id_env_two),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id/name in each dict
        data = response.data
        del data['environments'][0]['id']
        del data['environments'][0]['name']
        del data['environments'][1]['id']
        del data['environments'][1]['name']

        self.compare_json(name_file, data)

    def test_post_one_env_duplicate_error(self):
        """Test of error for post one duplicated environment."""

        name_file = 'api_environment/tests/sanity/json/post_one_env_duplicate_error.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)
