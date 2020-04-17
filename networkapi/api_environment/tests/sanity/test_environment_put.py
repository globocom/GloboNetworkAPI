# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentPutOneSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        'networkapi/api_environment/fixtures/initial_cidr.json',

    ]

    json_path = 'api_environment/tests/sanity/json/put/%s'

    comp_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_one_env(self):
        """Test of success to put 1 environment."""

        name_file = self.json_path % 'put_one_env.json'
        comp_file = self.comp_path % 'put_one_env.json'

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

        self.compare_json(comp_file, data)

    def test_put_one_env_new_configs(self):
        """Test of success to put 1 environment with new configs."""

        name_file = self.json_path % 'put_one_env_new_configs.json'
        get_file = self.comp_path % 'put_one_env_new_configs.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/1/?include=configs',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property name
        data = response.data
        del data['environments'][0]['name']
        del data['environments'][0]['configs'][0]['id']
        del data['environments'][0]['sdn_controllers']

        self.compare_json(get_file, data)

    def test_put_one_env_add_configs(self):
        """Test of success to put 1 environment with add configs."""

        name_file = self.json_path % 'put_one_env_add_configs.json'
        get_file = self.comp_path % 'put_one_env_add_configs.json'
        config_file = self.comp_path % 'put_one_env_add_configs-configs.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/1/?include=configs',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data
        del data['environments'][0]['name']
        del data['environments'][0]['configs']
        del data['environments'][0]['sdn_controllers']

        self.compare_json(get_file, data)

    def test_put_one_env_update_configs(self):
        """Test of success to put 1 environment with update configs."""

        name_file = self.json_path % 'put_one_env_update_configs.json'
        get_file = self.comp_path % 'put_one_env_update_configs.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/1/?include=configs',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property name
        data = response.data
        del data['environments'][0]['name']
        del data['environments'][0]['configs'][0]['id']
        del data['environments'][0]['sdn_controllers']
        self.compare_json(get_file, data)


class EnvironmentPutTwoSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
    ]

    json_path = 'api_environment/tests/sanity/json/put/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_two_env(self):
        """Test of success to put 2 environments."""

        name_file = self.json_path % 'put_two_env.json'

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


class EnvironmentPutErrorTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
    ]

    json_path = 'api_environment/tests/sanity/json/put/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_one_env_duplicate(self):
        """Test of error for put one duplicated environment."""

        name_file = self.json_path % 'put_one_env_duplicate_error.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)
