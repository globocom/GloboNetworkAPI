# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
import logging
from mock import patch, MagicMock
from rest_framework.test import APIClient
from networkapi.ambiente.models import Ambiente
from networkapi.equipamento.models import Equipamento
from networkapi.ip.models import NetworkIPv4, NetworkIPv6
from networkapi.test import mock_login
from networkapi.usuario.models import Usuario
from networkapi.vlan.models import Vlan

LOG = logging.getLogger(__name__)

class NetworkViewsTestCase(unittest.TestCase):

    def setUp(self):
        self.client = APIClient()
        self.mock_networkv4_get_by_pk()
        self.mock_networkv6_get_by_pk()

    def tearDown(self):
        pass

    @mock_login
    def test_network_ipv4_deploy_given_empty_equipment_list(self):
        response = self.post('/api/networkv4/1/equipments/', { 'equipments': ''})

        self.assertEqual(400, response.status_code, "Status code should be 400 and was %s" % response.status_code)
        self.assertEqual("Error validating request parameter: equipments", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv4_deploy_given_invalid_equipment_list(self):
        response = self.post('/api/networkv4/1/equipments/', { 'equipments': ['a']})

        self.assertEqual(400, response.status_code, "Status code should be 400 and was %s" % response.status_code)
        self.assertEqual("Error validating request parameter: equipments", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv4_deploy_given_no_equipments_found(self):
        self.mock_find_equipments([])
        response = self.post('/api/networkv4/1/equipments/', { 'equipments': [1, 2]})

        self.assertEqual("Equipments are not part of network environment.", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv4_deploy_given_no_routers_found_for_network_environment(self):
        self.mock_find_equipments(self.mock_distinct_list([]))
        response = self.post('/api/networkv4/1/equipments/')

        self.assertEqual("No environment routers found for network configuration.", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv4_deploy_given_user_without_permission(self):
        self.mock_find_equipments(self.mock_distinct_list([Equipamento(id = 1, nome = 'router')]))
        self.mock_user_has_permission(False)
        response = self.post('/api/networkv4/1/equipments/', None)

        self.assertEqual("No permission to configure equipment 1-router", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv4_deploy(self):
        equipment_list = [Equipamento(id=1, nome='router')]
        self.mock_find_equipments(self.mock_distinct_list(equipment_list))
        self.mock_user_has_permission(True)
        facade_mock = self.mock_equipment_script_facade_ipv4('DEPLOY')

        response = self.post('/api/networkv4/1/equipments/', None)

        facade_mock.assert_called_with(Usuario(), self.networkv4, equipment_list)
        self.assertEqual("Equipment configured", response.data, "Wrong status message")

    @mock_login
    def test_network_ipv4_deploy_given_equipments_supplied(self):
        equipment_list = [Equipamento(id=10, nome='router')]
        self.mock_user_has_permission(True)
        equipment_find_mock = self.mock_find_equipments(equipment_list)
        facade_mock = self.mock_equipment_script_facade_ipv4('DEPLOY')

        response = self.post('/api/networkv4/1/equipments/', {'equipments': [10]})

        equipment_find_mock.assert_called_with(equipamentoambiente__ambiente = self.networkv4.vlan.ambiente, id__in = [equip.id for equip in equipment_list])
        facade_mock.assert_called_with(Usuario(), self.networkv4, equipment_list)
        self.assertEqual("Equipment configured", response.data, "Wrong status message")

    @mock_login
    def test_network_ipv4_undeploy(self):
        equipment_list = [Equipamento(id=1, nome='router')]
        self.mock_find_equipments(self.mock_distinct_list(equipment_list))
        self.mock_user_has_permission(True)
        facade_mock = self.mock_equipment_script_facade_ipv4('UNDEPLOY')

        response = self.delete('/api/networkv4/1/equipments/', None)

        facade_mock.assert_called_with(Usuario(), self.networkv4, equipment_list)
        self.assertEqual("Equipment configured", response.data, "Wrong status message")

    @mock_login
    def test_network_ipv6_deploy_given_empty_equipment_list(self):
        response = self.post('/api/networkv6/1/equipments/', { 'equipments': ''})

        self.assertEqual(400, response.status_code, "Status code should be 400 and was %s" % response.status_code)
        self.assertEqual("Error validating request parameter: equipments", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv6_deploy_given_invalid_equipment_list(self):
        response = self.post('/api/networkv6/1/equipments/', { 'equipments': ['a']})

        self.assertEqual(400, response.status_code, "Status code should be 400 and was %s" % response.status_code)
        self.assertEqual("Error validating request parameter: equipments", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv6_deploy_given_no_equipments_found(self):
        self.mock_find_equipments([])
        response = self.post('/api/networkv6/1/equipments/', { 'equipments': [1, 2]})

        self.assertEqual("Equipments are not part of network environment.", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv6_deploy_given_no_routers_found_for_network_environment(self):
        self.mock_find_equipments(self.mock_distinct_list([]))
        response = self.post('/api/networkv6/1/equipments/')

        self.assertEqual("No environment routers found for network configuration.", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv6_deploy_given_user_without_permission(self):
        self.mock_find_equipments(self.mock_distinct_list([Equipamento(id = 1, nome = 'router')]))
        self.mock_user_has_permission(False)
        response = self.post('/api/networkv6/1/equipments/', None)

        self.assertEqual("No permission to configure equipment 1-router", response.data['detail'], "Wrong status message")

    @mock_login
    def test_network_ipv6_deploy(self):
        equipment_list = [Equipamento(id=1, nome='router')]
        self.mock_find_equipments(self.mock_distinct_list(equipment_list))
        self.mock_user_has_permission(True)
        facade_mock = self.mock_equipment_script_facade_ipv6('DEPLOY')

        response = self.post('/api/networkv6/1/equipments/', None)

        facade_mock.assert_called_with(Usuario(), self.networkv6, equipment_list)
        self.assertEqual("Equipment configured", response.data, "Wrong status message")

    @mock_login
    def test_network_ipv6_deploy_given_equipments_supplied(self):
        equipment_list = [Equipamento(id=10, nome='router')]
        self.mock_user_has_permission(True)
        equipment_find_mock = self.mock_find_equipments(equipment_list)
        facade_mock = self.mock_equipment_script_facade_ipv6('DEPLOY')

        response = self.post('/api/networkv6/1/equipments/', {'equipments': [10]})

        equipment_find_mock.assert_called_with(equipamentoambiente__ambiente = self.networkv6.vlan.ambiente, id__in = [equip.id for equip in equipment_list])
        facade_mock.assert_called_with(Usuario(), self.networkv6, equipment_list)
        self.assertEqual("Equipment configured", response.data, "Wrong status message")

    @mock_login
    def test_network_ipv6_undeploy(self):
        equipment_list = [Equipamento(id=1, nome='router')]
        self.mock_find_equipments(self.mock_distinct_list(equipment_list))
        self.mock_user_has_permission(True)
        facade_mock = self.mock_equipment_script_facade_ipv6('UNDEPLOY')

        response = self.delete('/api/networkv6/1/equipments/', None)

        facade_mock.assert_called_with(Usuario(), self.networkv6, equipment_list)
        self.assertEqual("Equipment configured", response.data, "Wrong status message")

    #MOCKS
    def mock_equipment_script_facade_ipv6(self, operation):
        return self.mock_equipment_script_facade(operation,'IPv6')

    def mock_equipment_script_facade_ipv4(self, operation):
        return self.mock_equipment_script_facade(operation, 'IPv4')

    def mock_equipment_script_facade(self, operation, type):
        if operation == 'DEPLOY':
            facade_mock = patch('networkapi.api_network.facade.deploy_network%s_configuration' % type).start()
        else:
            facade_mock = patch('networkapi.api_network.facade.remove_deploy_network%s_configuration' % type).start()
        facade_mock.return_value = "Equipment configured"
        return facade_mock

    def post(self, uri, content = None):
        return self.client.post(uri, content, format='json')

    def delete(self, uri, content = None):
        return self.client.delete(uri, content, format='json')

    def mock_distinct_list(self, list):
        mocked_list = MagicMock()
        mocked_list.distinct.return_value = list
        return mocked_list

    def mock_find_equipments(self, equipment_list):
        equipment_find_mock = patch('networkapi.equipamento.models.Equipamento.objects.filter').start()
        equipment_find_mock.return_value = equipment_list
        return equipment_find_mock

    def mock_networkv4_get_by_pk(self):
        network_mock = patch('networkapi.ip.models.NetworkIPv4').start()
        self.networkv4 = NetworkIPv4(vlan = Vlan(ambiente = Ambiente()))
        network_mock.get_by_pk = lambda network_id: self.networkv4
        return network_mock

    def mock_networkv6_get_by_pk(self):
        network_mock = patch('networkapi.ip.models.NetworkIPv6').start()
        self.networkv6 = NetworkIPv6(vlan = Vlan(ambiente = Ambiente()))
        network_mock.get_by_pk = lambda network_id: self.networkv6
        return network_mock

    def mock_user_has_permission(self, has_permission):
        permission_decorator = patch('networkapi.api_network.views.has_perm').start()
        permission_decorator.return_value = has_permission