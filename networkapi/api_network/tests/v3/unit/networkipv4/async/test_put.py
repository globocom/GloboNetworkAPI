# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.tasks import update_networkv4
from networkapi.ip.models import NetworkIPv4
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv4AsyncPutSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_netipv4_success(self):
        """Test success of id task generate for netipv4 put success."""

        user = Usuario(id=1, nome='test')

        net = NetworkIPv4(id=1)

        facade.update_networkipv4 = mock.MagicMock(return_value=net)
        facade.get_networkipv4_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        update_networkv4.update_state = mock.MagicMock()

        update_networkv4({'id': 1}, user.id)

        facade.update_networkipv4.assert_called_with({'id': 1}, user)


class NetworkIPv4AsyncPutErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_netipv4_error(self):
        """Test success of id task generate for netipv4 put error."""

        pass
