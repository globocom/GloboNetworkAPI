# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.api_ip import tasks
from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class IPv6AsyncDeleteSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/api_pools/fixtures/initial_optionspool.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/healthcheckexpect/fixtures/initial_healthcheck.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_ip/fixtures/initial_base.json',
        'networkapi/api_ip/fixtures/initial_base_v6.json',
        'networkapi/api_ip/fixtures/initial_pool.json',
        'networkapi/api_ip/fixtures/initial_vip_request_v6.json',
    ]

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_task_id_create_in_delete_one_ipv6_success(self):
        """Tests success of id task generate for ipv6 delete."""

        obj_id = 1
        response = tasks.update_ipv6.apply(args=[obj_id],
                                           queue='napi.network')

        id_task = response.id
        self.compare_values(36, len(id_task))
