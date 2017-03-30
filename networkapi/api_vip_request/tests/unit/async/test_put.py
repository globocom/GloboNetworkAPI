# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_vip_request.models import VipRequest
from networkapi.api_vip_request.tasks.deploy import redeploy
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class VipRequestAsyncPutDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_vip_request.facade.v3.update_real_vip_request')
    @patch('networkapi.api_vip_request.facade.v3.get_vip_request_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_vip_request.tasks.deploy.redeploy.update_state')
    def test_task_id_create_in_put_deploy_one_vip_request_success(self, *args):
        """Test success of id task generate for vip request put deploy success."""

        mock_get_user = args[1]
        mock_get_vip = args[2]
        mock_update_real_vip = args[3]

        user = Usuario(id=1, nome='test')

        vip = VipRequest(id=1)

        mock_update_real_vip.return_value = vip
        mock_get_vip.return_value = vip
        mock_get_user.return_value = user

        redeploy({'id': vip.id}, user.id)

        mock_update_real_vip.assert_called_with(
            [{'id': vip.id}], user)


class VipRequestAsyncPutDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_deploy_one_vip_request_error(self):
        """Test success of id task generate for vip request put deploy error."""

        pass
