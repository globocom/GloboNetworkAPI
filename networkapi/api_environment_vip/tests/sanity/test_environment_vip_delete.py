# -*- coding: utf-8 -*-
import logging

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class EnvironmentVipDeleteTestCase(NetworkApiTestCase):

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

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_delete_one_env_success(self):
        """Test of success to delete of one environment vip."""

        response = self.client.delete(
            '/api/v3/environment-vip/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v3/environment-vip/1/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

    def test_delete_one_env_inexistent_error(self):
        """Test of success to delete of one environment vip."""

        response = self.client.delete(
            '/api/v3/environment-vip/1000/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

    def test_delete_one_env_related_network_error(self):
        """Test of error to delete one environment vip related with network
        ipv4.
        """

        response = self.client.delete(
            '/api/v3/environment-vip/2/',
            content_type='application/json')

        self.compare_status(400, response.status_code)
