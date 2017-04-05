# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_network.tasks import update_networkv6
from networkapi.ip.models import NetworkIPv6
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv6AsyncPutSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.update_networkipv6')
    @patch('networkapi.api_network.facade.v3.get_networkipv6_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.update_networkv6.update_state')
    def test_task_id_create_in_put_one_netipv6_success(self, *args):
        """Test success of id task generate for netipv6 put success."""

        mock_get_user = args[1]
        mock_get_netv6 = args[2]
        mock_update_netv6 = args[3]

        user = Usuario(id=1, nome='test')

        net = NetworkIPv6(id=1)

        mock_update_netv6.return_value = net
        mock_get_netv6.return_value = net
        mock_get_user.return_value = user

        update_networkv6({'id': 1}, user.id)

        mock_update_netv6.assert_called_with({'id': 1}, user)


class NetworkIPv6AsyncPutErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_netipv6_error(self):
        """Test success of id task generate for netipv6 put error."""

        pass
