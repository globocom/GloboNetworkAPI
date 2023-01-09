# -*- coding: utf-8 -*-
import logging

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class EnvironmentDeleteTestCase(NetworkApiTestCase):

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

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_delete_one_env_success(self):
        """Test of success for delete one environment."""

        # Does post request
        response = self.client.delete(
            '/api/v3/environment/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/1/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

    def test_delete_two_env_success(self):
        """Test of success for delete two environments."""

        # Does post request
        response = self.client.delete(
            '/api/v3/environment/1;2/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/1;2/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

    def test_delete_one_env_inexistent_error(self):
        """Test of error for delete one inexistent environment."""

        # Does post request
        response = self.client.delete(
            '/api/v3/environment/1000/',
            content_type='application/json')

        # Tests code returned
        self.compare_status(404, response.status_code)

    def test_delete_two_env_inexistent_error(self):
        """Test of error for delete two inexistent environments."""

        # Does post request
        response = self.client.delete(
            '/api/v3/environment/1000;1001/',
            content_type='application/json')

        # Tests code returned
        self.compare_status(404, response.status_code)

    def test_delete_env_with_vlan_success(self):
        """Test of success for delete one environment with vlans."""

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/3/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # Does post request
        response = self.client.delete(
            '/api/v3/environment/3/',
            content_type='application/json')

        # Tests code returned
        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/3/',
            content_type='application/json')

        # Tests code returned
        self.compare_status(404, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/3/',
            content_type='application/json')

        # Tests code returned
        self.compare_status(404, response.status_code)
