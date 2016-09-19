# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


log = logging.getLogger(__name__)


class MockPlugin(object):

    _status = True

    @classmethod
    def status(cls, status=True):
        cls._status = status

    @classmethod
    def update_pool(cls, pools):
        if cls.status:
            log.info('Mock Update Pool')
        else:
            raise Exception('Erro')

    @classmethod
    def delete_pool(cls, pools):
        if cls.status:
            log.info('Mock Delete Pool')
        else:
            raise Exception('Erro')

    @classmethod
    def create_pool(cls, pools):
        if cls.status:
            log.info('Mock Create Pool')
        else:
            raise Exception('Erro')


class PoolDeployTestV3Case(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deploy_with_mock_success(self, test_patch):
        """
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mocked to test the flow in deploys
        """

        dp = self.load_json_file('api_pools/tests/json/test_pool_put_created.json')
        test_patch.return_value = MockPlugin()
        log.info(dp)
        facade_pool_deploy.update_real_pool(dp, self.user)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_create_deploy_with_mock_success(self, test_patch):
        """
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mocked to test the flow in deploys
        """

        dp = self.load_json_file('api_pools/tests/json/test_pool_post_mock_deploy.json')
        test_patch.return_value = MockPlugin()
        dp = dp.get('server_pools')
        facade_pool_deploy.create_real_pool(dp, self.user)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_create_deploy_with_mock_error(self, test_patch):
        """
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mocked to test the flow in deploys
        """

        dp = self.load_json_file('api_pools/tests/json/test_pool_post_mock_deploy.json')
        mock = MockPlugin()
        mock.status(False)
        test_patch.return_value = mock
        dp = dp.get('server_pools')
        self.assertRaises(
            Exception,
            facade_pool_deploy.create_real_pool(dp, self.user)
        )

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_create_deploy_with_mock_success_url(self, test_patch):
        """
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mocked to test the flow in deploys
        """
        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        # update
        response = self.client.post(
            '/api/v3/pool/deploy/1/',
            #  data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_post_mock_deploy.json')),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        log.info(response.data)
        self.assertEqual(200, response.status_code,
                         "Status code should be 200 and was %s" % response.status_code)
