# -*- coding: utf-8 -*-
import logging

from django.core.management import call_command
from django.test.client import Client
from mock import patch

from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
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


class PoolDeployMockPluginTestCase(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deploy_with_mock_success(self, test_patch):
        """
            Deploy update of one pool with success.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/unit/json/test_pool_put_created.json')
        test_patch.return_value = MockPlugin()
        dp = dp.get('server_pools')
        facade_pool_deploy.update_real_pool(dp, self.user)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deploy_with_mock_error(self, test_patch):
        """
            Deploy update of one pool with error.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/unit/json/test_pool_put_created.json')
        mock = MockPlugin()
        mock.status(False)
        test_patch.return_value = mock
        dp = dp.get('server_pools')
        self.assertRaises(
            Exception,
            facade_pool_deploy.delete_real_pool(dp, self.user)
        )

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_delete_deploy_with_mock_success(self, test_patch):
        """
            Deploy delete of one pool with success.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/unit/json/test_pool_delete_created.json')
        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock
        dp = dp.get('server_pools')
        self.assertRaises(
            Exception,
            facade_pool_deploy.delete_real_pool(dp, self.user)
        )

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_delete_deploy_with_mock_error(self, test_patch):
        """
            Deploy delete of one pool with error.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/unit/json/test_pool_delete_created.json')
        mock = MockPlugin()
        mock.status(False)
        test_patch.return_value = mock
        dp = dp.get('server_pools')
        self.assertRaises(
            Exception,
            facade_pool_deploy.delete_real_pool(dp, self.user)
        )

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_create_deploy_with_mock_success(self, test_patch):
        """
            Deploy create of one pool with success.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/unit/json/test_pool_post_not_created.json')
        test_patch.return_value = MockPlugin()
        dp = dp.get('server_pools')
        facade_pool_deploy.create_real_pool(dp, self.user)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_create_deploy_with_mock_error(self, test_patch):
        """
            Deploy create of one pool with error.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/unit/json/test_pool_post_not_created.json')
        mock = MockPlugin()
        mock.status(False)
        test_patch.return_value = mock
        dp = dp.get('server_pools')
        self.assertRaises(
            Exception,
            facade_pool_deploy.create_real_pool(dp, self.user)
        )
