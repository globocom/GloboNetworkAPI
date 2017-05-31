# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

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

    @patch('networkapi.api_vlan.facade.v3.delete_vlan')
    @patch('networkapi.api_vlan.facade.v3.get_vlan_by_id')
    @patch('networkapi.api_vlan.tasks.delete_vlan.update_state')
    def test_task_id_create_in_delete_one_vlan_success(self, *args):
        """Test success of id task generate for vlan delete success."""

        mock_get_vlan = args[1]
        mock_delete_vlan = args[2]

        vlan = Vlan(id=1)
        user = Usuario(id='1', nome='test')

        mock_delete_vlan.return_value = vlan
        mock_get_vlan.return_value = vlan

        delete_vlan(1, user.id)

        mock_delete_vlan.assert_called_with(1)


class VlanAsyncDeleteErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_vlan_error(self):
        """Test success of id task generate for vlan delete error."""

        pass
