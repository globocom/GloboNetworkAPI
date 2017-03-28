# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.api_ip import tasks
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from networkapi.util.geral import prepare_url

log = logging.getLogger(__name__)


class IPv4AsyncPostSuccessTestCase(NetworkApiTestCase):
    fixtures = [
        'networkapi/config/fixtures/initial_config.json',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_ip/fixtures/initial_base.json',
        'networkapi/api_ip/fixtures/initial_base_v4.json',
    ]

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    def test_task_id_create_in_post_one_ipv4_success(self):
        """Tests success of id task generate for ipv4 post."""

        name_file = 'api_ip/tests/sanity/ipv4/json/post/ipv4_auto_net_free.json'

        data = self.load_json_file(name_file)

        ipv4 = data['ips'][0]

        response = tasks.create_ipv4.apply(args=[ipv4, self.user.id],
                                           queue='napi.network')

        id_task = response.id
        self.compare_values(len(id_task), 36)
