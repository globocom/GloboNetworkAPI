# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

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

    @patch('networkapi.api_vlan.facade.v3.create_vlan')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_vlan.tasks.create_vlan.update_state')
    def test_task_id_create_in_post_one_vlan_success(self, *args):
        """Test success of id task generate for vlan post success."""

        mock_get_user = args[1]
        mock_create_vlan = args[2]

        user = Usuario(id=1, nome='test')
        vlan = Vlan(id=1)

        mock_create_vlan.return_value = vlan
        mock_get_user.return_value = user

        create_vlan({}, user.id)

        mock_create_vlan.assert_called_with({}, user)


class VlanAsyncPostErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_vlan_error(self):
        """Test success of id task generate for vlan post error."""

        pass
