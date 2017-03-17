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
        'networkapi/api_pools/fixtures/initial_pools_2.json',
        verbosity=0
    )


class PoolGetDeployMockTestCase(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    def mock_create_pool(self, id_pool, test_patch):

        pool = self.client.get(
            '/api/v3/pool/%s/' % id_pool,
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        test_patch.return_value = MockPlugin()

        facade_pool_deploy.create_real_pool(
            pool.data['server_pools'],
            self.user)

        pool = self.client.get(
            '/api/v3/pool/%s/' % id_pool,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        ).data['server_pools'][0]

        self.assertEqual(
            True,
            pool['pool_created'],
            'After deploy, flag created should be True.')

        pass

    def mock_delete_pool(self, id_pool, test_patch):

        pool = self.client.get(
            '/api/v3/pool/%s/' % id_pool,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')).data

        test_patch.return_value = MockPlugin()

        facade_pool_deploy.delete_real_pool(pool['server_pools'], self.user)

        pool = self.client.get(
            '/api/v3/pool/%s/' % id_pool,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')) \
            .data['server_pools'][0]

        self.assertEqual(
            False,
            pool['pool_created'],
            'After undeploy, flag created should be False.')

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_without_reals(self, test_patch):
        """Tries to deploy a pool without reals."""

        self.mock_create_pool(31, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_two_reals_and_tcp_protocol(self, test_patch):
        """Tries to deploy a pool with two reals and TCP protocol
        in healthcheck.
        """

        self.mock_create_pool(32, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_two_reals_and_https_protocol(self, test_patch):
        """Tries to deploy a pool with two reals and HTTPS protocol
        in healthcheck.
        """

        self.mock_create_pool(33, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_two_reals_and_udp_protocol(self, test_patch):
        """Tries to deploy a pool with two reals and UDP protocol
        in healthcheck.
        """

        self.mock_create_pool(34, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_two_reals_and_http_protocol(self, test_patch):
        """Tries to deploy a pool with two reals and HTTP protocol
        in healthcheck.
        """

        self.mock_create_pool(35, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_three_reals_and_weighted(self, test_patch):
        """Tries to deploy a pool with three reals and weighted balancing.
        """

        self.mock_create_pool(36, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_three_reals_and_least_conn(self, test_patch):
        """Tries to deploy a pool with three reals and least-conn balancing.
        """

        self.mock_create_pool(37, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deployed_pool_without_reals(self, test_patch):
        """Tries to update deployed pool without reals adding two reals to it.
        """

        id = 38

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')).data

        test_patch.return_value = MockPlugin()

        qt_reals = 2

        ipsv4 = [
            {'id': 45, 'ip_formated': '10.0.0.45'},
            {'id': 46, 'ip_formated': '10.0.0.46'}

        ]
        server_pool_members = [
            self.build_server_pool_member(
                ip__id=ipsv4[i]['id'],
                ip__ip_formated=ipsv4[i]['ip_formated'],
                port_real=8) for i in range(qt_reals)]

        pool['server_pools'][0]['server_pool_members'] = server_pool_members

        facade_pool_deploy.update_real_pool(pool['server_pools'], self.user)

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))\
            .data['server_pools'][0]

        self.assertEqual(2,
                         len(pool['server_pool_members']),
                         'This server pool should have two members.')
        self.assertEqual(
            True,
            pool['pool_created'],
            'After deploy, flag created should be True.')

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deployed_pool_with_reals_removing_them(self, test_patch):
        """Tries to update pool with reals removing them."""

        id = 39

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')).data

        test_patch.return_value = MockPlugin()

        pool['server_pools'][0]['server_pool_members'] = []

        facade_pool_deploy.update_real_pool(pool['server_pools'], self.user)

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')) \
            .data['server_pools'][0]

        self.assertEqual(0,
                         len(pool['server_pool_members']),
                         'This server pool should have zero members.')
        self.assertEqual(
            True,
            pool['pool_created'],
            'After deploy, flag created should be True.')

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deployed_pool_removing_half_of_reals(self, test_patch):
        """Tries to remove half of reals in a deployed server pool."""

        id = 40  # Pool with this ID has four members

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')).data

        self.assertEqual(4,
                         len(pool['server_pools'][0]['server_pool_members']),
                         'This server pool should have four members.')

        test_patch.return_value = MockPlugin()

        qt_reals = 2

        ipsv4 = [
            {'id': 49, 'ip_formated': '10.0.0.49'},
            {'id': 50, 'ip_formated': '10.0.0.50'}

        ]

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=ipsv4[i]['id'],
                ip__ip_formated=ipsv4[i]['ip_formated'],
                port_real=8) for i in range(qt_reals)]

        pool['server_pools'][0]['server_pool_members'] = server_pool_members

        facade_pool_deploy.update_real_pool(pool['server_pools'], self.user)

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')) \
            .data['server_pools'][0]

        self.assertEqual(2,
                         len(pool['server_pool_members']),
                         'This server pool should have two members.')
        self.assertEqual(
            True,
            pool['pool_created'],
            'After deploy, flag created should be True.')

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_update_deployed_pool_rm_half_reals_add_another(self, test_patch):
        """Tries to remove half of the reals in a deployed server pool and
        at same time adding a new real.
        """

        id = 41  # Pool with this ID has four members (IPs 53, 54, 55, 56)

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')).data

        self.assertEqual(4,
                         len(pool['server_pools'][0]['server_pool_members']),
                         'This server pool should have four members.')

        test_patch.return_value = MockPlugin()

        qt_reals = 3

        ipsv4 = [
            {'id': 53, 'ip_formated': '10.0.0.53'},
            {'id': 54, 'ip_formated': '10.0.0.54'},
            {'id': 57, 'ip_formated': '10.0.0.57'}

        ]

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=ipsv4[i]['id'],
                ip__ip_formated=ipsv4[i]['ip_formated'],
                port_real=8) for i in range(qt_reals)]

        pool['server_pools'][0]['server_pool_members'] = server_pool_members

        facade_pool_deploy.update_real_pool(pool['server_pools'], self.user)

        pool = self.client.get(
            '/api/v3/pool/%s/' % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')) \
            .data['server_pools'][0]

        self.assertEqual(3,
                         len(pool['server_pool_members']),
                         'This server pool should have three members.')
        self.assertEqual(
            True,
            pool['pool_created'],
            'After deploy, flag created should be True.')

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_undeploy_pool_with_reals(self, test_patch):
        """Tries to undeploy pool with two reals."""

        self.mock_delete_pool(42, test_patch)

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_undeploy_pool_without_reals(self, test_patch):
        """Tries to undeploy pool without reals."""

        self.mock_delete_pool(43, test_patch)

    def build_server_pool_member(self, **kwargs):

        ip__id = None
        ip__ip_formated = None

        ipv6__id = None
        ipv6__ip_formated = None

        port_real = None
        weight = None
        priority = None

        id = None

        for key in kwargs:

            if key == 'ip__id':
                ip__id = kwargs[key]
            elif key == 'ip__ip_formated':
                ip__ip_formated = kwargs[key]
            elif key == 'ipv6__id':
                ipv6__id = kwargs[key]
            elif key == 'ipv6__ip_formated':
                ipv6__ip_formated = kwargs[key]
            elif key == 'port_real':
                port_real = kwargs[key]
            elif key == 'weight':
                weight = kwargs[key]
            elif key == 'priority':
                priority = kwargs[key]
            elif key == 'id':
                id = kwargs[key]

        return {
            'id': id,
            'ip': {
                'id': ip__id,
                'ip_formated': ip__ip_formated
            } if ip__id is not None and ip__ip_formated is not None
            else None,
            'ipv6': {
                'id': ip__id,
                'ip_formated': ip__ip_formated
            } if ipv6__id is not None and ipv6__ip_formated is not None
            else None,
            'priority': priority if priority is not None else 0,
            'weight': weight if weight is not None else 0,
            'limit': 0,
            'port_real': port_real,
            'member_status': 7,
            'last_status_update_formated': None
        }
