# -*- coding: utf-8 -*-
import logging

import mock
from django.test.client import Client

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteLogico
from networkapi.ambiente.models import DivisaoDc
from networkapi.ambiente.models import GrupoL3
from networkapi.api_pools.facade.v3 import base as facade
from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.api_pools.models import OptionPool
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_pools.tasks.deploy import undeploy
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.requisicaovips.models import ServerPool
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


log = logging.getLogger(__name__)


class ServerPoolAsyncDeleteDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_server_pool_success(self):
        """Test success of id task generate for server pool delete deploy success."""

        user = Usuario(id=1, nome='test')

        divisaodc = DivisaoDc(id=1, nome='test')
        amblog = AmbienteLogico(id=1, nome='test')
        gl3 = GrupoL3(id=1, nome='test')
        ambiente = Ambiente(id=1, grupo_l3=gl3,
                            divisao_dc=divisaodc, ambiente_logico=amblog)

        optionpool = OptionPool(id=1, type='test', name='test')
        healthcheck = Healthcheck(id=1)
        pool = ServerPool(id=1, identifier='test', environment=ambiente, servicedownaction=optionpool,
                          healthcheck=healthcheck)

        pool_serializer = serializers.PoolV3Serializer(
            pool)

        facade_pool_deploy.delete_real_pool = mock.MagicMock(return_value=pool)
        facade.get_pool_by_id = mock.MagicMock(return_value=pool)
        Usuario.objects.get = mock.MagicMock(return_value=user)
        undeploy.update_state = mock.MagicMock()

        undeploy(pool.id, user.id)

        facade_pool_deploy.delete_real_pool.assert_called_with(
            [pool_serializer.data], user)


class ServerPoolAsyncDeleteDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_deploy_one_server_pool_error(self):
        """Test success of id task generate for server pool delete deploy error."""

        pass
