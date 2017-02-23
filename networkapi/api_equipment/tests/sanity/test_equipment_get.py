# -*- coding: utf-8 -*-
import logging

from django.core.management import call_command
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


def setup():
    call_command(
        'loaddata',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_equipment/fixtures/initial_pre_equipment.json',
        verbosity=0
    )


class EquipmentGetTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_equipment/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_list_equipment(self):
        """
        Test Success of get equipment list
        """

        response = self.client.get(
            '/api/v3/equipment/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )
