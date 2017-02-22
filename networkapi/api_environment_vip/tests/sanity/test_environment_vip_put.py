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
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        verbosity=0
    )


class EnvironmentVipPutSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_environment_vip/fixtures/initial_base.json',
    ]

    json_path = 'api_environment_vip/tests/sanity/json/put/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_one_env(self):
        """Test of success to put one environment vip."""

        name_file = self.json_path % 'put_one_envvip.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/2/?include=conf',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        data = response.data

        # Tests if data was updated
        self.compare_json(name_file, data)

    def test_put_one_env_add_environments(self):
        """Test of success to put one environment vip adding environments."""

        name_file = self.json_path % 'put_one_envvip_add_environments.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/2/?include=environments,conf',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        data = response.data

        # Tests if data was updated
        self.compare_json(name_file, data)

    def test_put_one_env_new_environments(self):
        """Test of success to put one environment vip with new environments."""

        name_file = self.json_path % 'put_one_envvip_new_environments.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/2/?include=environments,conf',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        data = response.data

        # Tests if data was updated
        self.compare_json(name_file, data)

    def test_put_one_env_update_environments(self):
        """Test of success to put one environment vip updating environments."""

        name_file = self.json_path % 'put_one_envvip_update_environments.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/2/?include=environments,conf',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        data = response.data

        # Tests if data was updated
        self.compare_json(name_file, data)

    def test_put_one_env_add_optionsvip(self):
        """Test of success to put one environment vip adding environments."""

        name_file = self.json_path % 'put_one_envvip_add_optionsvip.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/2/?include=optionsvip,conf',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        data = response.data

        # Tests if data was updated
        self.compare_json(name_file, data)

    def test_put_one_env_new_optionsvip(self):
        """Test of success to put one environment vip with new environments."""

        name_file = self.json_path % 'put_one_envvip_new_optionsvip.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/2/?include=optionsvip,conf',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        data = response.data

        # Tests if data was updated
        self.compare_json(name_file, data)

    def test_put_one_env_update_optionsvip(self):
        """Test of success to put one environment vip updating environments."""

        name_file = self.json_path % 'put_one_envvip_update_optionsvip.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/2/?include=optionsvip,conf',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.compare_status(200, response.status_code)

        data = response.data

        # Tests if data was updated
        self.compare_json(name_file, data)
