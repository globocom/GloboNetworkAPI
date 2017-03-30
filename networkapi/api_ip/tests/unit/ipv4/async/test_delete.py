# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_ip import facade
from networkapi.api_ip.tasks import delete_ipv4
from networkapi.ip.models import Ip
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


log = logging.getLogger(__name__)


class IPv4AsyncDeleteSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_ipv4_success(self):
        """Test success of id task generate for ipv4 delete success."""

        ipv4 = Ip(id=1)

        facade.delete_ipv4 = mock.MagicMock(return_value=ipv4)
        facade.get_ipv4_by_id = mock.MagicMock(return_value=ipv4)
        delete_ipv4.update_state = mock.MagicMock()

        delete_ipv4(1)

        facade.delete_ipv4.assert_called_with(1)


class IPv4AsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_ipv4_error(self):
        """Test success of id task generate for ipv4 delete error."""

        pass
