# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_ip.tasks import update_ipv4
from networkapi.ip.models import Ip
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class IPv4AsyncPutSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_ip.facade.update_ipv4')
    @patch('networkapi.api_ip.facade.get_ipv4_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_ip.tasks.update_ipv4.update_state')
    def test_task_id_create_in_put_one_ipv4_success(self, *args):
        """Test success of id task generate for ipv4 put success."""

        mock_get_user = args[1]
        mock_get_ipv4 = args[2]
        mock_update_ipv4 = args[3]

        ipv4 = Ip(id=1)
        user = Usuario(id=1, nome='test')

        mock_update_ipv4.return_value = ipv4
        mock_get_ipv4.return_value = ipv4
        mock_get_user.return_value = user

        update_ipv4({'id': 1}, user.id)

        mock_update_ipv4.assert_called_with({'id': 1}, user)


class IPv4AsyncPutErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_ipv4_error(self):
        """Test success of id task generate for ipv4 put error."""

        pass
