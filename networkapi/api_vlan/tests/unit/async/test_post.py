# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_vlan.facade import v3 as facade
from networkapi.api_vlan.tasks import create_vlan
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from networkapi.vlan.models import Vlan


log = logging.getLogger(__name__)


class VlanAsyncPostSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_vlan_success(self):
        """Test success of id task generate for vlan post success."""

        user = Usuario(id=1, nome='test')
        vlan = Vlan(id=1)

        facade.create_vlan = mock.MagicMock(return_value=vlan)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        create_vlan.update_state = mock.MagicMock()

        create_vlan({}, user.id)

        facade.create_vlan.assert_called_with({}, user)


class VlanAsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_vlan_error(self):
        """Test success of id task generate for vlan post error."""

        pass
