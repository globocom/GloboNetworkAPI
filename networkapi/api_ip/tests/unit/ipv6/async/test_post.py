# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_ip.tasks import create_ipv6
from networkapi.ip.models import Ip
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class IPv6AsyncPostSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_ip.facade.create_ipv6')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_ip.tasks.create_ipv6.update_state')
    def test_task_id_create_in_post_one_ipv6_success(self, *args):
        """Test success of id task generate for ipv6 post success."""

        mock_get_user = args[1]
        mock_create_ipv6 = args[2]

        ipv6 = Ip(id=1)
        user = Usuario(id=1, nome='test')

        mock_create_ipv6.return_value = ipv6
        mock_get_user.return_value = user

        create_ipv6({}, user.id)

        mock_create_ipv6.assert_called_with({}, user)


class IPv6AsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_ipv6_error(self):
        """Test success of id task generate for ipv6 post error."""

        pass
