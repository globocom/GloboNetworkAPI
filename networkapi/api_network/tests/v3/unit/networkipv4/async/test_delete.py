# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.tasks import delete_networkv4
from networkapi.api_network.tasks import undeploy_networkv4
from networkapi.ip.models import NetworkIPv4
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv4AsyncDeleteSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_netipv4_success(self):
        """Test success of id task generate for netipv4 delete success."""

        net = NetworkIPv4(id=1)

        facade.delete_networkipv4 = mock.MagicMock(return_value=net)
        facade.get_networkipv4_by_id = mock.MagicMock(return_value=net)
        delete_networkv4.update_state = mock.MagicMock()

        delete_networkv4(1)

        facade.delete_networkipv4.assert_called_with(1)


class NetworkIPv4AsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_netipv4_error(self):
        """Test success of id task generate for netipv4 delete error."""

        pass


class NetworkIPv4AsyncDeleteDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_netipv4_success(self):
        """Test success of id task generate for netipv4 delete deploy success."""

        net = NetworkIPv4(id=1)
        user = Usuario(id='1', nome='test')

        facade.undeploy_networkipv4 = mock.MagicMock(return_value=net)
        facade.get_networkipv4_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        undeploy_networkv4.update_state = mock.MagicMock()

        undeploy_networkv4(net.id, user.id)

        facade.undeploy_networkipv4.assert_called_with(net.id, user)


class NetworkIPv4AsyncDeleteDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_netipv4_error(self):
        """Test success of id task generate for netipv4 delete deploy error."""

        pass
