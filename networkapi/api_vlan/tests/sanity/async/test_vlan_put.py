# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.api_vlan import tasks
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


log = logging.getLogger(__name__)


class VlanAsyncPutTestCase(NetworkApiTestCase):

    fixtures = [
        'loaddata',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/api_vlan/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    def test_task_id_create_in_put_one_vlan_success(self):
        """Test success of id task generate for vlan put."""

        name_file = 'api_vlan/tests/sanity/json/put/put_one_vlan.json'

        data = self.load_json_file(name_file)

        vlan = data['vlans'][0]

        response = tasks.update_vlan.apply(args=[vlan, self.user.id],
                                           queue='napi.network')

        id_task = response.id
        self.compare_values(36, len(id_task))
