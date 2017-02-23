# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentVipPostSuccessTestCase(NetworkApiTestCase):
    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/api_environment_vip/fixtures/initial_base.json',
    ]

    json_path = 'api_environment_vip/tests/sanity/json/post/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_env(self):
        """Test of success to post one environment vip."""

        name_file = self.json_path % 'post_one_envvip.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment-vip/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/%s/?include=conf' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['environments_vip'][0]['id']

        self.compare_json(name_file, data)

    def test_post_one_env_with_environments(self):
        """Test of success to post one environment vip with environments."""

        name_file = self.json_path % 'post_one_envvip_with_environments.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment-vip/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/%s/?include=environments,conf' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['environments_vip'][0]['id']

        self.compare_json(name_file, data)

    def test_post_one_env_with_optionsvip(self):
        """Test of success to post one environment vip with options vip."""

        name_file = self.json_path % 'post_one_envvip_with_optionsvip.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment-vip/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/%s/?include=optionsvip,conf' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['environments_vip'][0]['id']

        self.compare_json(name_file, data)
