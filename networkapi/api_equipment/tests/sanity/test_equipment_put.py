# -*- coding: utf-8 -*-
import json
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
        'networkapi/api_equipment/fixtures/initial_base.json',
        verbosity=0
    )


class EquipmentPutTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_one_equipment_success(self):
        """Test Success of put of one equipment."""

        name_file = 'api_equipment/tests/sanity/json/put_one_equipment.json'

        # Does put request
        response = self.client.put(
            '/api/v3/equipment/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/equipment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        data = response.data
        print json.dumps(self.load_json_file(name_file), sort_keys=True)
        print json.dumps(data, sort_keys=True)

        # Tests if data was updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )
