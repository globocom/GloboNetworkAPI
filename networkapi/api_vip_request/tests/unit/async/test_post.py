# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_vip_request.models import VipRequest
from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer
from networkapi.api_vip_request.tasks.deploy import deploy
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class VipRequestAsyncPostDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_vip_request.facade.v3.create_real_vip_request')
    @patch('networkapi.api_vip_request.facade.v3.get_vip_request_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_vip_request.tasks.deploy.deploy.update_state')
    def test_task_id_create_in_post_deploy_one_vip_request_success(self, *args):
        """Test success of id task generate for vip request post deploy success."""

        mock_get_user = args[1]
        mock_get_vip = args[2]
        mock_create_real_vip = args[3]

        user = Usuario(id=1, nome='test')

        vip = VipRequest(id=1)
        vip_serializer = VipRequestV3Serializer(
            vip, include=('ports__identifier',))

        mock_create_real_vip.return_value = vip
        mock_get_vip.return_value = vip
        mock_get_user.return_value = user

        deploy(vip.id, user.id)

        mock_create_real_vip.assert_called_with(
            [vip_serializer.data], user)


class VipRequestAsyncPostDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_vip_request_error(self):
        """Test success of id task generate for vip request post deploy error."""

        pass
