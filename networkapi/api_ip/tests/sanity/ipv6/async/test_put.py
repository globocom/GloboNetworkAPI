# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.api_ip import tasks
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from networkapi.util.geral import prepare_url


log = logging.getLogger(__name__)


class IPv6AsyncPutSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_ip/fixtures/initial_base.json',
        'networkapi/api_ip/fixtures/initial_base_v6.json',
    ]

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_ipv6_success(self):
        """Tests success of id task generate for ipv6 put."""

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_1_net_5_eqpt_1.json'

        data = self.load_json_file(name_file)

        ipv6 = data['ips'][0]

        response = tasks.update_ipv6.apply(args=[ipv6, self.user.id],
                                           queue='napi.network')

        id_task = response.id
        self.compare_values(len(id_task), 36)
