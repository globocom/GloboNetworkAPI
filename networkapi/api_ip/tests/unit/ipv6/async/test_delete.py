# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_ip.tasks import delete_ipv6
from networkapi.ip.models import Ip
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class IPv6AsyncDeleteSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_ip.facade.delete_ipv6')
    @patch('networkapi.api_ip.facade.get_ipv6_by_id')
    @patch('networkapi.api_ip.tasks.delete_ipv6.update_state')
    def test_task_id_create_in_delete_one_ipv6_success(self, *args):
        """Test success of id task generate for ipv6 delete success."""

        mock_get_ipv6 = args[1]
        mock_delete_ipv6 = args[2]

        ipv6 = Ip(id=1)
        user = Usuario(id='1', nome='test')

        mock_delete_ipv6.return_value = ipv6
        mock_get_ipv6.return_value = ipv6

        delete_ipv6(1, user.id)

        mock_delete_ipv6.assert_called_with(1)


class IPv6AsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_ipv6_error(self):
        """Test success of id task generate for ipv6 delete error."""

        pass
