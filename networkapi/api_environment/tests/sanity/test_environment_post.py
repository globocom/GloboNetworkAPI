# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentPostOneSuccessTestCase(NetworkApiTestCase):

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
    ]

    json_path = 'api_environment/tests/sanity/json/post/%s'
    get_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_env(self):
        """Test of success to post 1 environment."""

        name_file = self.json_path % 'post_one_env.json'
        get_file = self.get_path % 'post_one_env.json'

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
        del data['environments'][0]['sdn_controllers']

        self.compare_json(get_file, data)

    def test_post_one_env_with_father_environment(self):
        """Test of success to post 1 environment with father environment."""

        name_file = self.json_path % 'post_one_env_with_father.json'
        get_file = self.get_path % 'post_one_env_with_father.json'

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
        del data['environments'][0]['sdn_controllers']

        self.compare_json(get_file, data)

    def test_post_one_env_with_configs(self):
        """Test of success to post 1 environment with configs."""

        name_file = self.json_path % 'post_one_env_with_configs.json'
        get_file = self.get_path % 'post_one_env_with_configs.json'

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
            '/api/v3/environment/%s/?include=configs' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id/name/sdn_controllers
        data = response.data
        del data['environments'][0]['id']
        del data['environments'][0]['configs'][0]['id']
        del data['environments'][0]['name']
        del data['environments'][0]['sdn_controllers']

        self.compare_json(get_file, data)


class EnvironmentPostTwoSuccessTestCase(NetworkApiTestCase):

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
    ]

    json_path = 'api_environment/tests/sanity/json/post/%s'
    comp_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_two_env(self):
        """Test of success to post 2 environments."""

        name_file = self.json_path % 'post_two_env.json'
        com_file = self.comp_path % 'post_two_env.json'

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
        del data['environments'][0]['sdn_controllers']

        del data['environments'][1]['id']
        del data['environments'][1]['name']
        del data['environments'][1]['sdn_controllers']

        self.compare_json(com_file, data)

    def test_post_two_env_with_father_environment(self):
        """Test of success to post 2 environments with father environment."""

        name_file = self.json_path % 'post_two_env_with_father.json'
        com_file = self.comp_path % 'post_two_env_with_father.json'

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

        # Removes property id/name/sdn_controllers in each dict
        data = response.data
        del data['environments'][0]['id']
        del data['environments'][0]['name']
        del data['environments'][0]['sdn_controllers']
        del data['environments'][1]['id']
        del data['environments'][1]['name']
        del data['environments'][1]['sdn_controllers']

        self.compare_json(com_file, data)

    def test_post_two_env_with_configs(self):
        """Test of success to post 2 environments with configs."""

        name_file = self.json_path % 'post_two_env_with_configs.json'
        com_file = self.comp_path % 'post_two_env_with_configs.json'

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
            '/api/v3/environment/%s;%s/?include=configs' % (
                id_env_one, id_env_two),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id/name/sdn_controllers in each dict
        data = response.data
        del data['environments'][0]['id']
        del data['environments'][0]['configs'][0]['id']
        del data['environments'][0]['name']
        del data['environments'][0]['sdn_controllers']
        del data['environments'][1]['id']
        del data['environments'][1]['configs'][0]['id']
        del data['environments'][1]['name']
        del data['environments'][1]['sdn_controllers']

        self.compare_json(com_file, data)


class EnvironmentPostErrorTestCase(NetworkApiTestCase):

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

    json_path = 'api_environment/tests/sanity/json/post/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_env_duplicate(self):
        """Test of error for post one duplicated environment."""

        name_file = self.json_path % 'post_one_env_duplicate_error.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        self.compare_values(
            'Causa: None, Mensagem: Duplicate Environment.',
            response.data['detail'])

    def test_post_two_env_with_invalid_father_environment(self):
        """Test of error for post one environment with invalid father
            environment.
        """

        name_file = self.json_path % 'post_one_env_with_invalid_father.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        self.compare_values(
            'Causa: , Mensagem: There is no environment with id = 100.',
            response.data['detail'])
