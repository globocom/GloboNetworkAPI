# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteLogico
from networkapi.ambiente.models import DivisaoDc
from networkapi.ambiente.models import GrupoL3
from networkapi.api_pools.facade.v3 import base as facade_base
from networkapi.api_pools.facade.v3 import deploy as facade_deploy
from networkapi.api_pools.tasks.deploy import redeploy
from networkapi.requisicaovips.models import ServerPool
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class ServerPoolAsyncPutDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_deploy_one_server_pool_success(self):
        """Test success of id task generate for server pool put deploy success."""

        user = Usuario(id=1, nome='test')

        divisaodc = DivisaoDc(id=1, nome='test')
        amblog = AmbienteLogico(id=1, nome='test')
        gl3 = GrupoL3(id=1, nome='test')
        ambiente = Ambiente(id=1, grupo_l3=gl3,
                            divisao_dc=divisaodc, ambiente_logico=amblog)

        pool = ServerPool(id=1, identifier='test', environment=ambiente)

        with mock.patch.object(facade_deploy, 'update_real_pool', return_value=pool) \
                as mock_deploy:
            with mock.patch.object(facade_base, 'get_pool_by_id', return_value=pool):
                with mock.patch.object(Usuario.objects, 'get', return_value=user):
                    with mock.patch.object(redeploy, 'update_state'):
                        redeploy({'id': pool.id}, user.id)

        mock_deploy.assert_called_with([{'id': pool.id}], user)


class ServerPoolAsyncPutDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_put_deploy_one_server_pool_error(self):
        """Test success of id task generate for server pool put deploy error."""

        pass
