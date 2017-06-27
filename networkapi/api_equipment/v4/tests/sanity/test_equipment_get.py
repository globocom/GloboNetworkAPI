# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)

json_path = 'api_equipment/v4/tests/sanity/json/%s'

class EquipmentGetTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_equipment/v4/fixtures/initial_pre_equipment.json',
        'networkapi/api_equipment/v4/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_success_list_equipment(self):
        """
        Test of success to get equipment list
        """

        response = self.client.get(
            '/api/v4/equipment/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_equipment_with_as_id(self):
        """Test of success to get equipment with as id."""

        name_file = json_path % 'get/basic/pk_4.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/equipment/4/?include=id_as',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['equipments'])

    def test_get_equipment_with_as_details(self):
        """Test of success to get equipment with as details."""

        name_file = json_path % 'get/details/pk_4.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/equipment/4/?include=id_as__details',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['equipments'])
