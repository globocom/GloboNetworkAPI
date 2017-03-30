# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.tasks import create_networkv4
from networkapi.api_network.tasks import deploy_networkv4
from networkapi.ip.models import NetworkIPv4
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv4AsyncPostSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_netipv4_success(self):
        """Test success of id task generate for netipv4 post success."""

        user = Usuario(id=1, nome='test')

        net = NetworkIPv4(id=1)

        facade.create_networkipv4 = mock.MagicMock(return_value=net)
        facade.get_networkipv4_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        create_networkv4.update_state = mock.MagicMock()

        create_networkv4({}, user.id)

        facade.create_networkipv4.assert_called_with({}, user)


class NetworkIPv4AsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_netipv4_error(self):
        """Test success of id task generate for netipv4 post error."""

        pass


class NetworkIPv4AsyncPostDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_netipv4_success(self):
        """Test success of id task generate for netipv4 post deploy success."""

        user = Usuario(id=1, nome='test')

        net = NetworkIPv4(id=1)

        facade.deploy_networkipv4 = mock.MagicMock(return_value=net)
        facade.get_networkipv4_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        deploy_networkv4.update_state = mock.MagicMock()

        deploy_networkv4(net.id, user.id)

        facade.deploy_networkipv4.assert_called_with(net.id, user)


class NetworkIPv4AsyncPostDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_netipv4_error(self):
        """Test success of id task generate for netipv4 post deploy error."""

        pass
