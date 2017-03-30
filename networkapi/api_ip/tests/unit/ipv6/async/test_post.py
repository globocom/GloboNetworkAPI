# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_ip import facade
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

    def test_task_id_create_in_post_one_ipv6_success(self):
        """Test success of id task generate for ipv6 post success."""

        ipv6 = Ip(id=1)
        user = Usuario(id=1, nome='test')

        facade.create_ipv6 = mock.MagicMock(return_value=ipv6)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        create_ipv6.update_state = mock.MagicMock()

        create_ipv6({}, user.id)

        facade.create_ipv6.assert_called_with({}, user)


class IPv6AsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_ipv6_error(self):
        """Test success of id task generate for ipv6 post error."""

        pass
