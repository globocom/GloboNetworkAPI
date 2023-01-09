# -*- coding: utf-8 -*-
import logging

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class CIDRDeleteTestCase(NetworkApiTestCase):

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

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_delete_one_cidr_success(self):
        """Test of success for delete one cidr."""

        # Does post request
        response = self.client.delete(
            '/api/v3/cidr/5/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/cidr/5/',
            content_type='application/json')

        self.compare_status(400, response.status_code)

    def test_delete_two_cidr_success(self):
        """Test of success for delete two cidr."""

        # Does post request
        response = self.client.delete(
            '/api/v3/cidr/4;6/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/cidr/4;6/',
            content_type='application/json')

        self.compare_status(400, response.status_code)

    def test_delete_cidr_by_env_success(self):
        """Test of success for delete all cidr linked to an environment."""

        # Does post request
        response = self.client.delete(
            '/api/v3/cidr/environment/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/cidr/2;3/',
            content_type='application/json')

        self.compare_status(400, response.status_code)

    def test_delete_one_cidr_inexistent_error(self):
        """Test of error for delete one inexistent cidr."""

        # Does post request
        response = self.client.delete(
            '/api/v3/cidr/1000/',
            content_type='application/json')

        # Tests code returned
        self.compare_status(400, response.status_code)

    def test_delete_two_cidr_inexistent_error(self):
        """Test of error for delete two inexistent cidr."""

        # Does post request
        response = self.client.delete(
            '/api/v3/cidr/1000;1001/',
            content_type='application/json')

        # Tests code returned
        self.compare_status(400, response.status_code)
