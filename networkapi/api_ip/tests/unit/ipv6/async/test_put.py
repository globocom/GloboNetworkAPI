# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_ip import facade
from networkapi.api_ip.tasks import update_ipv6
from networkapi.ip.models import Ip
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class IPv6AsyncPutSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_ipv6_success(self):
        """Test success of id task generate for ipv6 put success."""

        ipv6 = Ip(id=1)
        user = Usuario(id=1, nome='test')

        facade.update_ipv6 = mock.MagicMock(return_value=ipv6)
        facade.get_ipv6_by_id = mock.MagicMock(return_value=ipv6)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        update_ipv6.update_state = mock.MagicMock()

        update_ipv6({'id': 1}, user.id)

        facade.update_ipv6.assert_called_with({'id': 1}, user)


class IPv6AsyncPutErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_ipv6_error(self):
        """Test success of id task generate for ipv6 put error."""

        pass
