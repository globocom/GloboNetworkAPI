# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from nose.tools import assert_equal
from nose.tools import assert_in
from nose.tools import assert_is_instance
from nose.tools import assert_raises

from mock import patch

from api_tests.api_mock.mock import MockPlugin

from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.usuario.models import Usuario

from networkapiclient.ClientFactory import ClientFactory
from networkapiclient.exception import NetworkAPIClientError


NETWORKAPI_URL = os.getenv('NETWORKAPI_URL', 'http://10.0.0.2:8000/')
NETWORKAPI_USER = os.getenv('NETWORKAPI_USER', 'networkapi')
NETWORKAPI_PWD = os.getenv('NETWORKAPI_PWD', 'networkapi')


class TestApiPoolDeploy(TestCase):

    def setUp(self):
        self.client = ClientFactory(NETWORKAPI_URL, NETWORKAPI_USER,
                                    NETWORKAPI_PWD)
        self.api_pool = self.client.create_api_pool()
        self.api_pool_deploy = self.client.create_api_pool_deploy()

        self.ipsv4 = [{'id': 7, 'ip_formated': '192.168.104.2'},
                      {'id': 8, 'ip_formated': '192.168.104.3'},
                      {'id': 9, 'ip_formated': '192.168.104.4'},
                      {'id': 10, 'ip_formated': '192.168.104.5'},
                      {'id': 11, 'ip_formated': '192.168.104.6'}]

        self.user = Usuario(id=1, nome='networkapi')

        self.id_env_of_pool = 10

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_without_reals(self, test_patch):
        """ Tries to deploy a pool without reals """

        test_patch.return_value = MockPlugin()

        pool_data = self.build_pool(id_env_of_pool=10)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool_data['id'] = pool_id

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_one_real_and_https_protocol(self, test_patch):
        """ Tries to deploy a pool with one real and HTTPS protocol in healthcheck """

        test_patch.return_value = MockPlugin()

        qt_reals = range(1)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                          i) for i in qt_reals]

        healthcheck_healthcheck_type = 'HTTPS'

        pool_data = self.build_pool(
            server_pool_members=server_pool_members,
            healthcheck__healthcheck_type=healthcheck_healthcheck_type,
            id_env_of_pool=self.id_env_of_pool)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool_data['id'] = pool_id

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)
        assert_equal(
            pool['server_pools'][0]['healthcheck']['healthcheck_type'],
            healthcheck_healthcheck_type)

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_one_real_and_tcp_protocol(self, test_patch):
        """ Tries to deploy a pool with one real and TCP protocol in healthcheck """

        test_patch.return_value = MockPlugin()

        qt_reals = range(1)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                          i) for i in qt_reals]

        healthcheck_healthcheck_type = 'TCP'

        pool_data = self.build_pool(
            server_pool_members=server_pool_members,
            healthcheck__healthcheck_type=healthcheck_healthcheck_type,
            id_env_of_pool=self.id_env_of_pool)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)
        assert_equal(
            pool['server_pools'][0]['healthcheck']['healthcheck_type'],
            healthcheck_healthcheck_type)

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_one_real_and_udp_protocol(self, test_patch):
        """ Tries to deploy a pool with one real and UDP protocol in healthcheck """

        test_patch.return_value = MockPlugin()

        qt_reals = range(1)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                          i) for i in qt_reals]

        healthcheck_healthcheck_type = 'UDP'

        pool_data = self.build_pool(
            server_pool_members=server_pool_members,
            healthcheck__healthcheck_type=healthcheck_healthcheck_type,
            id_env_of_pool=self.id_env_of_pool)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)
        assert_equal(
            pool['server_pools'][0]['healthcheck']['healthcheck_type'],
            healthcheck_healthcheck_type)

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_one_real_and_http_protocol(self, test_patch):
        """ Tries to deploy a pool with one real and HTTP protocol in healthcheck """

        test_patch.return_value = MockPlugin()

        qt_reals = range(1)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                          i) for i in qt_reals]

        healthcheck_healthcheck_type = 'HTTP'

        pool_data = self.build_pool(
            server_pool_members=server_pool_members,
            healthcheck__healthcheck_type=healthcheck_healthcheck_type,
            id_env_of_pool=self.id_env_of_pool)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)
        assert_equal(
            pool['server_pools'][0]['healthcheck']['healthcheck_type'],
            healthcheck_healthcheck_type)

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_three_reals_and_weight_balancing(self, test_patch):
        """ Tries to deploy a pool with three reals and weight balancing """

        test_patch.return_value = MockPlugin()

        qt_reals = range(3)
        weights = [1,2,1]

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 + i,
                weight=weights[i]) for i in qt_reals]

        pool_data = self.build_pool(
            server_pool_members=server_pool_members,
            id_env_of_pool=self.id_env_of_pool)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_with_three_reals_and_least_conn_balancing(self, test_patch):
        """ Tries to deploy a pool with three reals and least-conn balancing """

        test_patch.return_value = MockPlugin()

        qt_reals = range(3)

        priorities = [1,2,1]

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 + i,
                priority=priorities[i]) for i in qt_reals]

        pool_data = self.build_pool(
            server_pool_members=server_pool_members,
            id_env_of_pool=self.id_env_of_pool)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_update_pool_without_reals(self, test_patch):
        """ Tries to update deployed pool without reals adding two reals to it """
        test_patch.return_value = MockPlugin()

        qt_reals = range(2)

        pool_data = self.build_pool(
            id_env_of_pool=self.id_env_of_pool)
        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                i) for i in qt_reals]

        pool['server_pools'][0]['servicedownaction']['name'] = 'drop'
        pool['server_pools'][0]['healthcheck']['healthcheck_type'] = 'HTTPS'
        pool['server_pools'][0]['server_pool_members'] = server_pool_members

        facade_pool_deploy.update_real_pool(pool, self.user)

        pool_updated = self.api_pool.get([pool_id])['server_pools'][0]

        assert_equal(
            pool_updated['servicedownaction']['name'],
            pool['server_pools'][0]['servicedownaction']['name'])
        assert_equal(
            pool_updated['healthcheck']['healthcheck_type'],
            pool['server_pools'][0]['healthcheck']['healthcheck_type'])

        assert_equal(len(pool_updated['server_pool_members']), 2)

        # self.api_pool_deploy.delete([pool_id])
        # self.api_pool.delete([pool_id])

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_update_pool_with_reals_removing_them_after(self, test_patch):
        """ Tries to update deployed pool with reals removing them after """
        test_patch.return_value = MockPlugin()

        qt_reals = range(2)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                i) for i in qt_reals]

        pool_data = self.build_pool(
            id_env_of_pool=self.id_env_of_pool,
            server_pool_members=server_pool_members)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        facade_pool_deploy.create_real_pool(pool['server_pools'], self.user)

        pool['server_pools'][0]['server_pool_members'] = []

        facade_pool_deploy.update_real_pool(pool, self.user)

        pool_updated = self.api_pool.get([pool_id])['server_pools'][0]

        assert_equal(len(pool_updated['server_pool_members']), 0)

        # self.api_pool_deploy.delete([pool_id])
        # self.api_pool.delete([pool_id])

    def test_deploy_update_pool_removing_half_of_reals(self):
        """ Tries to remove half of the reals in a deployed server pool """

        qt_reals = range(4)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                i) for i in qt_reals]

        pool_data = self.build_pool(
            id_env_of_pool=self.id_env_of_pool,
            server_pool_members=server_pool_members)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        self.api_pool_deploy.create([pool_id])

        half = range(2)
        for i in half:
            server_pool_members.pop()

        new_pool_data = self.build_pool(
            id=pool_id,
            id_env_of_pool=self.id_env_of_pool,
            server_pool_members=server_pool_members)

        self.api_pool_deploy.update([new_pool_data])

        pool = self.api_pool.get([pool_id])['server_pools'][0]

        assert_equal(len(pool['server_pool_members']), 2)

        self.api_pool_deploy.delete([pool_id])

        self.api_pool.delete([pool_id])

    def test_deploy_update_pool_removing_half_of_reals_and_adding_another(self):
        """ Tries to remove half of the reals in a deployed server pool and at same time add a new real """

        qt_reals = range(5)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                i) for i in range(4)]

        pool_data = self.build_pool(
            id_env_of_pool=self.id_env_of_pool,
            server_pool_members=server_pool_members)

        pool_id = self.api_pool.create([pool_data])[0]['id']
        self.api_pool_deploy.create([pool_id])

        half = range(2)
        for i in half:
            server_pool_members.pop()

        server_pool_members += [self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                i) for i in range(4,5)]

        new_pool_data = self.build_pool(
            id=pool_id,
            id_env_of_pool=self.id_env_of_pool,
            server_pool_members=server_pool_members)


        self.api_pool_deploy.update([new_pool_data])

        pool = self.api_pool.get([pool_id])['server_pools'][0]

        assert_equal(len(pool['server_pool_members']), 3)

        self.api_pool_deploy.delete([pool_id])
        self.api_pool.delete([pool_id])




    def test_undeploy_pool_without_reals(self):
        """ Tries to undeploy a pool without reals """

        pool_data = self.build_pool(id_env_of_pool=1)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)

        self.api_pool_deploy.create([pool_id])

        self.api_pool_deploy.delete([pool_id])

        self.api_pool.delete([pool_id])

    def test_undeploy_pool_with_reals(self):
        """ Tries to undeploy a pool with two reals """

        qt_reals = range(2)

        server_pool_members = [
            self.build_server_pool_member(
                ip__id=self.ipsv4[i]['id'],
                ip__ip_formated=self.ipsv4[i]['ip_formated'],
                port_real=1000 +
                          i) for i in qt_reals]

        healthcheck_healthcheck_type = 'HTTP'

        pool_data = self.build_pool(
            server_pool_members=server_pool_members,
            healthcheck__healthcheck_type=healthcheck_healthcheck_type,
            id_env_of_pool=self.id_env_of_pool)

        pool_id = self.api_pool.create([pool_data])[0]['id']

        pool = self.api_pool.get([pool_id])

        assert_equal(pool['server_pools'][0]['id'], pool_id)
        assert_equal(
            pool['server_pools'][0]['healthcheck']['healthcheck_type'],
            healthcheck_healthcheck_type)

        self.api_pool_deploy.create([pool_id])

        self.api_pool_deploy.delete([pool_id])

        self.api_pool.delete([pool_id])

    def build_pool(self, **kwargs):

        id_env_of_pool = None
        healthcheck__healthcheck_type = None
        server_pool_members = None
        id = None
        identifier = None
        servicedownaction__name = None

        for key in kwargs:
            if key == 'id_env_of_pool':
                id_env_of_pool = kwargs[key]
            elif key == 'healthcheck__healthcheck_type':
                healthcheck__healthcheck_type = kwargs[key]
            elif key == 'server_pool_members':
                server_pool_members = kwargs[key]
            elif key == 'id':
                id = kwargs[key]
            elif key == 'identifier':
                identifier = kwargs[key]
            elif key == 'servicedownaction__name':
                servicedownaction__name = kwargs[key]

        return {
            'id': id,
            'identifier': identifier if identifier is not None else 'Pool-Test',
            'default_port': 443,
            'environment': id_env_of_pool,
            'servicedownaction': {
                'name': servicedownaction__name
                if servicedownaction__name is not None
                else 'none'
            },
            'lb_method': 'least-conn',
            'healthcheck': {
                'identifier': 'Test-Network-API-Ident',
                'healthcheck_type': healthcheck__healthcheck_type
                if healthcheck__healthcheck_type is not None
                else 'HTTP',
                'healthcheck_request': '',
                'healthcheck_expect': '',
                'destination': '*:*'},
            'default_limit': 0,
            'server_pool_members': server_pool_members
            if server_pool_members is not None
            else []
        }

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
            } if ip__id is not None and ip__ip_formated is not None else None,
            'ipv6': {
                'id': ip__id,
                'ip_formated': ip__ip_formated
            } if ipv6__id is not None and ipv6__ip_formated is not None else None,
            'priority': priority if priority is not None else 0,
            'weight': weight if weight is not None else 0,
            'limit': 0,
            'port_real': port_real,
            'member_status': 7,
            'last_status_update_formated': None
        }
