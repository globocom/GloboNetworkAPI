# -*- coding: utf-8 -*-
import logging

from mock import patch
from networkapi.api_network.tasks import delete_networkv4, undeploy_networkv4
from networkapi.ip.models import NetworkIPv4
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class NetworkIPv4AsyncDeleteSuccessTestCase(NetworkApiTestCase):

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

    @patch('networkapi.api_network.facade.v3.delete_networkipv4')
    @patch('networkapi.api_network.facade.v3.get_networkipv4_by_id')
    @patch('networkapi.api_network.tasks.delete_networkv4.update_state')
    def test_task_id_create_in_delete_one_netipv4_success(self, *args):
        """Test success of id task generate for netipv4 delete success."""

        mock_get_netv4 = args[1]
        mock_delete_netv4 = args[2]

        net = NetworkIPv4(id=1)
        user = Usuario(id='1', nome='test')

        mock_delete_netv4.return_value = net
        mock_get_netv4.return_value = net

        delete_networkv4(1, user.id)

        mock_delete_netv4.assert_called_with(1)


class NetworkIPv4AsyncDeleteErrorTestCase(NetworkApiTestCase):

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

    def test_task_id_create_in_delete_one_netipv4_error(self):
        """Test success of id task generate for netipv4 delete error."""

        pass


class NetworkIPv4AsyncDeleteDeploySuccessTestCase(NetworkApiTestCase):

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

    @patch('networkapi.api_network.facade.v3.undeploy_networkipv4')
    @patch('networkapi.api_network.facade.v3.get_networkipv4_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_network.tasks.undeploy_networkv4.update_state')
    def test_task_id_create_in_delete_deploy_one_netipv4_success(self, *args):
        """Test success of id task generate for netipv4 delete deploy success."""

        mock_get_user = args[1]
        mock_get_netv4 = args[2]
        mock_undeploy_netv4 = args[3]

        net = NetworkIPv4(id=1)
        user = Usuario(id='1', nome='test')

        mock_undeploy_netv4.return_value = net
        mock_get_netv4.return_value = net
        mock_get_user.return_value = user

        undeploy_networkv4(net.id, user.id)

        mock_undeploy_netv4.assert_called_with(net.id, user)


class NetworkIPv4AsyncDeleteDeployErrorTestCase(NetworkApiTestCase):

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

    def test_task_id_create_in_delete_deploy_one_netipv4_error(self):
        """Test success of id task generate for netipv4 delete deploy error."""

        pass
