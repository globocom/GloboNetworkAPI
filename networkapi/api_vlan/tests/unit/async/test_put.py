# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_vlan.facade import v3 as facade
from networkapi.api_vlan.tasks import update_vlan
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from networkapi.vlan.models import Vlan

log = logging.getLogger(__name__)


class VlanAsyncPutSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_vlan_success(self):
        """Test success of id task generate for vlan put success."""

        user = Usuario(id=1, nome='test')
        vlan = Vlan(id=1)

        facade.update_vlan = mock.MagicMock(return_value=vlan)
        facade.get_vlan_by_id = mock.MagicMock(return_value=vlan)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        update_vlan.update_state = mock.MagicMock()

        update_vlan({'id': 1}, user.id)

        facade.update_vlan.assert_called_with({'id': 1}, user)


class VlanAsyncPutErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_vlan_error(self):
        """Test success of id task generate for vlan put error."""

        pass
