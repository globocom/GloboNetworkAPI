# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

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

    @patch('networkapi.api_vlan.facade.v3.update_vlan')
    @patch('networkapi.api_vlan.facade.v3.get_vlan_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_vlan.tasks.update_vlan.update_state')
    def test_task_id_create_in_put_one_vlan_success(self, *args):
        """Test success of id task generate for vlan put success."""

        mock_get_user = args[1]
        mock_get_vlan = args[2]
        mock_update_vlan = args[3]

        user = Usuario(id=1, nome='test')
        vlan = Vlan(id=1)

        mock_update_vlan.return_value = vlan
        mock_get_vlan.return_value = vlan
        mock_get_user.return_value = user

        update_vlan({'id': 1}, user.id)

        mock_update_vlan.assert_called_with({'id': 1}, user)


class VlanAsyncPutErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_vlan_error(self):
        """Test success of id task generate for vlan put error."""

        pass
