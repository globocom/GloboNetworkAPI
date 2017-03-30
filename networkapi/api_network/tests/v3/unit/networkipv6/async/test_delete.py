# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.tasks import delete_networkv6
from networkapi.api_network.tasks import undeploy_networkv6
from networkapi.ip.models import NetworkIPv6
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv6AsyncDeleteSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_netipv6_success(self):
        """Test success of id task generate for netipv6 delete success."""

        net = NetworkIPv6(id=1)

        facade.delete_networkipv6 = mock.MagicMock(return_value=net)
        facade.get_networkipv6_by_id = mock.MagicMock(return_value=net)
        delete_networkv6.update_state = mock.MagicMock()

        delete_networkv6(1)

        facade.delete_networkipv6.assert_called_with(1)


class NetworkIPv6AsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_netipv6_error(self):
        """Test success of id task generate for netipv6 delete error."""

        pass


class NetworkIPv6AsyncDeleteDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_netipv6_success(self):
        """Test success of id task generate for netipv6 delete deploy success."""

        net = NetworkIPv6(id=1)
        user = Usuario(id='1', nome='test')

        facade.undeploy_networkipv6 = mock.MagicMock(return_value=net)
        facade.get_networkipv6_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        undeploy_networkv6.update_state = mock.MagicMock()

        undeploy_networkv6(net.id, user.id)

        facade.undeploy_networkipv6.assert_called_with(net.id, user)


class NetworkIPv6AsyncDeleteDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_netipv6_error(self):
        """Test success of id task generate for netipv6 delete deploy error."""

        pass
