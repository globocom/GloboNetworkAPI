# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_ip import facade
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

    def test_task_id_create_in_delete_one_ipv6_success(self):
        """Test success of id task generate for ipv6 delete success."""

        ipv6 = Ip(id=1)

        facade.delete_ipv6 = mock.MagicMock(return_value=ipv6)
        facade.get_ipv6_by_id = mock.MagicMock(return_value=ipv6)
        delete_ipv6.update_state = mock.MagicMock()

        delete_ipv6(1)

        facade.delete_ipv6.assert_called_with(1)


class IPv6AsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_ipv6_error(self):
        """Test success of id task generate for ipv6 delete error."""

        pass
