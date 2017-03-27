# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class VipRequestAsyncPostTestCase(NetworkApiTestCase):

    fixtures = [
        'loaddata',
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
        'networkapi/api_vip_request/fixtures/initial_base_environment.json',
        'networkapi/api_vip_request/fixtures/initial_base_pool.json'
    ]

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    def test_post_two_vips_success(self):
        """Test of success to post one vip."""

        name_file = 'api_vip_request/tests/sanity/json/test_vip_request_post_2_ports.json'

        data = self.load_json_file(name_file)

        vlan = data['vlans'][0]

        response = tasks.create_vlan.apply(args=[vlan, self.user.id],
                                           queue='napi.vip')

        id_task = response.id

        self.compare_values(len(id_task), 36)
