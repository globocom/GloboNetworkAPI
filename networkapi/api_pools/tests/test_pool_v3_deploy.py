# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.test.mock import MockPlugin
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


log = logging.getLogger(__name__)


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
            Deploy update of one pool with success.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/json/test_pool_put_created.json')
        test_patch.return_value = MockPlugin()
        log.info(dp)
        facade_pool_deploy.update_real_pool(dp, self.user)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deploy_with_mock_error(self, test_patch):
        """
            Deploy update of one pool with error.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool.
        """

        dp = self.load_json_file(
            'api_pools/tests/json/test_pool_put_created.json')
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
            'api_pools/tests/json/test_pool_delete_created.json')
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
            'api_pools/tests/json/test_pool_delete_created.json')
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
            'api_pools/tests/json/test_pool_post_not_created.json')
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
            'api_pools/tests/json/test_pool_post_not_created.json')
        mock = MockPlugin()
        mock.status(False)
        test_patch.return_value = mock
        dp = dp.get('server_pools')
        self.assertRaises(
            Exception,
            facade_pool_deploy.create_real_pool(dp, self.user)
        )

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deploy_with_mock_success_url(self, test_patch):
        """
            Deploy update of one pool with success by url.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool by url.
        """
        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        # update
        response = self.client.put(
            '/api/v3/pool/deploy/5/',
            data=json.dumps(self.load_json_file(
                'api_pools/tests/json/test_pool_put_created.json')),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        log.info(response.data)
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_delete_deploy_with_mock_success_url(self, test_patch):
        """
            Deploy delete of one pool with success by url.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool by url.
        """
        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        # update
        response = self.client.delete(
            '/api/v3/pool/deploy/5/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        log.info(response.data)
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_create_deploy_with_mock_success_url(self, test_patch):
        """
            Deploy create of one pool with success by url.
            Method that factory in networkapi.plugins.factory.PluginFactory
            is mock to test the flow in deploys of pool by url.
        """
        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        # update
        response = self.client.post(
            '/api/v3/pool/deploy/8/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        log.info(response.data)
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deploy_with_reals_success(self, test_patch):
        """
        """
        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        # update
        response = self.client.put(
            '/api/v3/pool/deploy/10/',
            data=json.dumps(self.load_json_file(
                'api_pools/tests/json/test_pool_put_created_with_reals.json')),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        log.info(response.data)
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' % response.status_code)
