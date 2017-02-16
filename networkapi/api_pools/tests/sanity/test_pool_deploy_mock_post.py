# -*- coding: utf-8 -*-
import logging

from django.core.management import call_command
from django.test.client import Client
from mock import patch

from networkapi.test.mock import MockPlugin
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


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


class PoolDeployMockPostTestCase(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_create_deploy_with_mock_success_url(self, test_patch):
        """Deploy create of one pool with success by url.

            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool by url.
        """
        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        name_file = 'api_pools/tests/sanity/json/mock/pool_2_created.json'

        response = self.client.post(
            '/api/v3/pool/deploy/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        response = self.client.get(
            '/api/v3/pool/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)
