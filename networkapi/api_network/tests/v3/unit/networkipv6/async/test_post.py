# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.tasks import create_networkv6
from networkapi.api_network.tasks import deploy_networkv6
from networkapi.ip.models import NetworkIPv6
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class NetworkIPv6AsyncPostSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_netipv6_success(self):
        """Test success of id task generate for netipv6 post success."""

        user = Usuario(id=1, nome='test')

        net = NetworkIPv6(id=1)

        facade.create_networkipv6 = mock.MagicMock(return_value=net)
        facade.get_networkipv6_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        create_networkv6.update_state = mock.MagicMock()

        create_networkv6({}, user.id)

        facade.create_networkipv6.assert_called_with({}, user)


class NetworkIPv6AsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_netipv6_error(self):
        """Test success of id task generate for netipv6 post error."""

        pass


class NetworkIPv6AsyncPostDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_netipv6_success(self):
        """Test success of id task generate for netipv6 post deploy success."""

        user = Usuario(id=1, nome='test')

        net = NetworkIPv6(id=1)

        facade.deploy_networkipv6 = mock.MagicMock(return_value=net)
        facade.get_networkipv6_by_id = mock.MagicMock(return_value=net)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        deploy_networkv6.update_state = mock.MagicMock()

        deploy_networkv6(net.id, user.id)

        facade.deploy_networkipv6.assert_called_with(net.id, user)


class NetworkIPv6AsyncPostDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_netipv6_error(self):
        """Test success of id task generate for netipv6 post deploy error."""

        pass
