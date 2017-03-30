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

        with mock.patch.object(facade, 'delete_real_vip_request', return_value=vip) \
                as mock_deploy:
            with mock.patch.object(facade, 'get_vip_request_by_id', return_value=vip):
                with mock.patch.object(Usuario.objects, 'get', return_value=user):
                    with mock.patch.object(undeploy, 'update_state'):
                        undeploy(vip.id, user.id)

        mock_deploy.assert_called_with([vip_serializer.data], user)


class VipRequestAsyncDeleteDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_vip_request_error(self):
        """Test success of id task generate for vip request delete deploy error."""

        pass
