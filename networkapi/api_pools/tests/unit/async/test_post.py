# -*- coding: utf-8 -*-
import logging

from django.test.client import Client
from mock import patch

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteLogico
from networkapi.ambiente.models import DivisaoDc
from networkapi.ambiente.models import GrupoL3
from networkapi.api_pools.models import OptionPool
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_pools.tasks.deploy import deploy
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.requisicaovips.models import ServerPool
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
log = logging.getLogger(__name__)


class ServerPoolAsyncPostDeploySuccessTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('networkapi.api_pools.facade.v3.deploy.create_real_pool')
    @patch('networkapi.api_pools.facade.v3.base.get_pool_by_id')
    @patch('networkapi.usuario.models.Usuario.objects.get')
    @patch('networkapi.api_pools.tasks.deploy.deploy.update_state')
    def test_task_id_create_in_post_deploy_one_server_pool_success(self, *args):
        """Test success of id task generate for server pool post deploy success."""

        mock_get_user = args[1]
        mock_get_pool = args[2]
        mock_create_real_pool = args[3]

        user = Usuario(id=1, nome='test')

        divisaodc = DivisaoDc(id=1, nome='test')
        amblog = AmbienteLogico(id=1, nome='test')
        gl3 = GrupoL3(id=1, nome='test')
        ambiente = Ambiente(id=1, grupo_l3=gl3,
                            divisao_dc=divisaodc, ambiente_logico=amblog)

        optionpool = OptionPool(id=1, type='test', name='test')
        healthcheck = Healthcheck(id=1)
        pool = ServerPool(id=1, identifier='test', environment=ambiente,
                          servicedownaction=optionpool, healthcheck=healthcheck)

        pool_serializer = serializers.PoolV3Serializer(
            pool)

        mock_create_real_pool.return_value = pool
        mock_get_pool.return_value = pool
        mock_get_user.return_value = user

        deploy(pool.id, user.id)

        mock_create_real_pool.assert_called_with(
            [pool_serializer.data], user)


class ServerPoolAsyncPostDeployErrorTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_post_deploy_one_server_pool_error(self):
        """Test success of id task generate for server pool post deploy error."""

        pass
