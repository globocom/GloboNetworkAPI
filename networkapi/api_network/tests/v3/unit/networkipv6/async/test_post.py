# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_network.tasks import create_networkv6
from networkapi.api_network.tasks import deploy_networkv6
from networkapi.ip.models import NetworkIPv6
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv6AsyncPostSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.create_networkipv6')
    @patch('networkapi.api_network.facade.v3.get_networkipv6_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.create_networkv6.update_state')
    def test_task_id_create_in_post_one_netipv6_success(self, *args):
        """Test success of id task generate for netipv6 post success."""

        mock_get_user = args[1]
        mock_get_netv6 = args[2]
        mock_create_netv6 = args[3]

        user = Usuario(id=1, nome='test')

        net = NetworkIPv6(id=1)

        mock_create_netv6.return_value = net
        mock_get_netv6.return_value = net
        mock_get_user.return_value = user

        create_networkv6({}, user.id)

        mock_create_netv6.assert_called_with({}, user)


class NetworkIPv6AsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_netipv6_error(self):
        """Test success of id task generate for netipv6 post error."""

        pass


class NetworkIPv6AsyncPostDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.deploy_networkipv6')
    @patch('networkapi.api_network.facade.v3.get_networkipv6_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.deploy_networkv6.update_state')
    def test_task_id_create_in_post_deploy_one_netipv6_success(self, *args):
        """Test success of id task generate for netipv6 post deploy success."""

        mock_get_user = args[1]
        mock_get_netv6 = args[2]
        mock_deploy_netv6 = args[3]

        user = Usuario(id=1, nome='test')

        net = NetworkIPv6(id=1)

        mock_deploy_netv6.return_value = net
        mock_get_netv6.return_value = net
        mock_get_user.return_value = user

        deploy_networkv6(net.id, user.id)

        mock_deploy_netv6.assert_called_with(net.id, user)


class NetworkIPv6AsyncPostDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_netipv6_error(self):
        """Test success of id task generate for netipv6 post deploy error."""

        pass
