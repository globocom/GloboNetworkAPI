# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_network.tasks import delete_networkv6
from networkapi.api_network.tasks import undeploy_networkv6
from networkapi.ip.models import NetworkIPv6
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv6AsyncDeleteSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.delete_networkipv6')
    @patch('networkapi.api_network.facade.v3.get_networkipv6_by_id')
    @patch('networkapi.api_network.tasks.delete_networkv6.update_state')
    def test_task_id_create_in_delete_one_netipv6_success(self, *args):
        """Test success of id task generate for netipv6 delete success."""

        mock_get_netv6 = args[1]
        mock_delete_netv6 = args[2]

        net = NetworkIPv6(id=1)
        user = Usuario(id='1', nome='test')

        mock_delete_netv6.return_value = net
        mock_get_netv6.return_value = net

        delete_networkv6(1, user.id)

        mock_delete_netv6.assert_called_with(1)


class NetworkIPv6AsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_netipv6_error(self):
        """Test success of id task generate for netipv6 delete error."""

        pass


class NetworkIPv6AsyncDeleteDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.undeploy_networkipv6')
    @patch('networkapi.api_network.facade.v3.get_networkipv6_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.undeploy_networkv6.update_state')
    def test_task_id_create_in_delete_deploy_one_netipv6_success(self, *args):
        """Test success of id task generate for netipv6 delete deploy success."""

        mock_get_user = args[1]
        mock_get_netv6 = args[2]
        mock_undeploy_netv6 = args[3]

        net = NetworkIPv6(id=1)
        user = Usuario(id='1', nome='test')

        mock_undeploy_netv6.return_value = net
        mock_get_netv6.return_value = net
        mock_get_user.return_value = user

        undeploy_networkv6(net.id, user.id)

        mock_undeploy_netv6.assert_called_with(net.id, user)


class NetworkIPv6AsyncDeleteDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_netipv6_error(self):
        """Test success of id task generate for netipv6 delete deploy error."""

        pass
