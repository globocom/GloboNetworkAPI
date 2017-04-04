# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_network.tasks import create_networkv4
from networkapi.api_network.tasks import deploy_networkv4
from networkapi.ip.models import NetworkIPv4
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv4AsyncPostSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.create_networkipv4')
    @patch('networkapi.api_network.facade.v3.get_networkipv4_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.create_networkv4.update_state')
    def test_task_id_create_in_post_one_netipv4_success(self, *args):
        """Test success of id task generate for netipv4 post success."""

        mock_get_user = args[1]
        mock_get_netv4 = args[2]
        mock_create_netv4 = args[3]

        user = Usuario(id=1, nome='test')

        net = NetworkIPv4(id=1)

        mock_create_netv4.return_value = net
        mock_get_netv4.return_value = net
        mock_get_user.return_value = user

        create_networkv4({}, user.id)

        mock_create_netv4.assert_called_with({}, user)


class NetworkIPv4AsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_netipv4_error(self):
        """Test success of id task generate for netipv4 post error."""

        pass


class NetworkIPv4AsyncPostDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.deploy_networkipv4')
    @patch('networkapi.api_network.facade.v3.get_networkipv4_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.deploy_networkv4.update_state')
    def test_task_id_create_in_post_deploy_one_netipv4_success(self, *args):
        """Test success of id task generate for netipv4 post deploy success."""

        mock_get_user = args[1]
        mock_get_netv4 = args[2]
        mock_deploy_netv4 = args[3]

        user = Usuario(id=1, nome='test')

        net = NetworkIPv4(id=1)

        mock_deploy_netv4.return_value = net
        mock_get_netv4.return_value = net
        mock_get_user.return_value = user

        deploy_networkv4(net.id, user.id)

        mock_deploy_netv4.assert_called_with(net.id, user)


class NetworkIPv4AsyncPostDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_netipv4_error(self):
        """Test success of id task generate for netipv4 post deploy error."""

        pass
