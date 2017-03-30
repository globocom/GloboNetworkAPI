# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_network.facade import v3 as facade
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

    def test_task_id_create_in_put_one_netipv6_success(self):
        """Test success of id task generate for netipv6 put success."""

        user = Usuario(id=1, nome='test')

        net = NetworkIPv6(id=1)

        facade.update_networkipv6 = mock.MagicMock(return_value=net)
        facade.get_networkipv6_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        update_networkv6.update_state = mock.MagicMock()

        update_networkv6({'id': 1}, user.id)

        facade.update_networkipv6.assert_called_with({'id': 1}, user)


class NetworkIPv6AsyncPutErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_netipv6_error(self):
        """Test success of id task generate for netipv6 put error."""

        pass
