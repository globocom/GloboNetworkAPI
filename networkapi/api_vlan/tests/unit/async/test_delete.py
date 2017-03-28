# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_vlan.facade import v3 as facade
from networkapi.api_vlan.tasks import delete_vlan
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from networkapi.vlan.models import Vlan


log = logging.getLogger(__name__)


class VlanAsyncDeleteSuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_vlan_success(self):
        """Test success of id task generate for vlan delete success."""

        vlan = Vlan(id=1)

        facade.delete_vlan = mock.MagicMock(return_value=vlan)
        facade.get_vlan_by_id = mock.MagicMock(return_value=vlan)
        delete_vlan.update_state = mock.MagicMock()

        delete_vlan(1)

        facade.delete_vlan.assert_called_with(1)


class VlanAsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_vlan_error(self):
        """Test success of id task generate for vlan delete error."""

        pass
