# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.api_vip_request.facade import v3 as facade
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

    def test_task_id_create_in_put_deploy_one_vip_request_success(self):
        """Test success of id task generate for vip request put deploy success."""

        user = Usuario(id=1, nome='test')

        vip = VipRequest(id=1)

        with mock.patch.object(facade, 'update_real_vip_request', return_value=vip) \
                as mock_deploy:
            with mock.patch.object(facade, 'get_vip_request_by_id', return_value=vip):
                with mock.patch.object(Usuario.objects, 'get', return_value=user):
                    with mock.patch.object(redeploy, 'update_state'):
                        redeploy({'id': vip.id}, user.id)

        mock_deploy.assert_called_with([{'id': vip.id}], user)


class VipRequestAsyncPutDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_deploy_one_vip_request_error(self):
        """Test success of id task generate for vip request put deploy error."""

        pass
