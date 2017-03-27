# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.api_vlan import tasks
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


log = logging.getLogger(__name__)


class VlanAsyncDeleteTestCase(NetworkApiTestCase):

    fixtures = [
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

    def test_task_id_create_in_delete_one_vlan_success(self):
        """Test success of id task generate for vlan delete."""

        obj_id = 1
        response = tasks.delete_vlan.apply(args=[obj_id],
                                           queue='napi.vip')

        id_task = response.id
        self.compare_values(36, len(id_task))
