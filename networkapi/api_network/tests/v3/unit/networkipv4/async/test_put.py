# -*- coding: utf-8 -*-
import logging

from mock import patch
from networkapi.api_network.tasks import update_networkv4
from networkapi.ip.models import NetworkIPv4
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class NetworkIPv4AsyncPutSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    @patch('networkapi.api_network.facade.v3.update_networkipv4')
    @patch('networkapi.api_network.facade.v3.get_networkipv4_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.update_networkv4.update_state')
    def test_task_id_create_in_put_one_netipv4_success(self, *args):
        """Test success of id task generate for netipv4 put success."""

        mock_get_user = args[1]
        mock_get_netv4 = args[2]
        mock_update_netv4 = args[3]

        user = Usuario(id=1, nome='test')

        net = NetworkIPv4(id=1)

        mock_update_netv4.return_value = net
        mock_get_netv4.return_value = net
        mock_get_user.return_value = user

        update_networkv4({'id': 1}, user.id)

        mock_update_netv4.assert_called_with({'id': 1}, user)


class NetworkIPv4AsyncPutErrorTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)
    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_netipv4_error(self):
        """Test success of id task generate for netipv4 put error."""

        pass
