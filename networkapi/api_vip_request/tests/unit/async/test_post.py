# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_vip_request.facade import v3 as facade
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

    def test_task_id_create_in_post_deploy_one_vip_request_success(self):
        """Test success of id task generate for vip request post deploy success."""

        user = Usuario(id=1, nome='test')

        vip = VipRequest(id=1)
        vip_serializer = VipRequestV3Serializer(
            vip, include=('ports__identifier',))

        facade.create_real_vip_request = mock.MagicMock(return_value=vip)
        facade.get_vip_request_by_id = mock.MagicMock(return_value=vip)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        deploy.update_state = mock.MagicMock()

        deploy(vip.id, user.id)

        facade.create_real_vip_request.assert_called_with(
            [vip_serializer.data], user)


class VipRequestAsyncPostDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_vip_request_error(self):
        """Test success of id task generate for vip request post deploy error."""

        pass
