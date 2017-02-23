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


class EquipmentDeleteTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_equipment/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_delete_one_equipment_success(self):
        """Test success of delete of one equipment."""

        response = self.client.delete(
            '/api/v3/equipment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v3/equipment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Dont there is a equipament by pk = 1.',
            response.data['detail'])


class EquipmentDeleteErrorTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_equipment/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_delete_one_inexistent_equipment(self):
        """Test success of delete of one equipment."""

        response = self.client.delete(
            '/api/v3/equipment/10/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Dont there is a equipament by pk = 10.',
            response.data['detail'])
