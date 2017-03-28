# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_vip_request.facade import v3 as facade
from networkapi.api_vip_request.models import VipRequest
from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer
from networkapi.api_vip_request.tasks.deploy import undeploy
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class VipRequestAsyncDeleteDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_vip_request_success(self):
        """Test success of id task generate for vip request delete deploy success."""

        user = Usuario(id=1, nome='test')

        vip = VipRequest(id=1)
        vip_serializer = VipRequestV3Serializer(
            vip, include=('ports__identifier',))

        facade.delete_real_vip_request = mock.MagicMock(return_value=vip)
        facade.get_vip_request_by_id = mock.MagicMock(return_value=vip)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        undeploy.update_state = mock.MagicMock()

        undeploy(vip.id, user.id)

        facade.delete_real_vip_request.assert_called_with(
            [vip_serializer.data], user)


class VipRequestAsyncDeleteDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_vip_request_error(self):
        """Test success of id task generate for vip request delete deploy error."""

        pass
