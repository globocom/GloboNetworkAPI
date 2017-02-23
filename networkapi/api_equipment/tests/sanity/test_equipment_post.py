# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EquipmentPostSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_equipment/fixtures/initial_pre_equipment.json',
    ]

    json_path = 'api_equipment/tests/sanity/json/post/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_equipment(self):
        """Test of success to post one equipment."""

        name_file = self.json_path % 'post_one_equipment.json'

        # Does post request
        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/equipment/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data
        del data['equipments'][0]['id']

        self.compare_json(name_file, data)

    def test_post_one_equipment_with_groups(self):
        """Test of success to post one equipment with groups."""

        name_file = self.json_path % 'post_one_equipment_with_groups.json'

        # Does post request
        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/equipment/%s/?include=groups' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data
        del data['equipments'][0]['id']

        self.compare_json(name_file, data)

    def test_post_one_equipment_with_environments(self):
        """Test of success to post one equipment with environments."""

        name_file = self.json_path % 'post_one_equipment_with_environments.json'

        # Does post request
        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/equipment/%s/?include=environments' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data
        del data['equipments'][0]['id']

        self.compare_json(name_file, data)


class EquipmentPostErrorTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_equipment/fixtures/initial_pre_equipment.json',
        'networkapi/api_equipment/fixtures/initial_base.json',
    ]

    json_path = 'api_equipment/tests/sanity/json/post/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_duplicated_equipment(self):
        """Test of error to post of one equipment with name already existent."""

        name_file = self.json_path % 'post_one_duplicated_equipment.json'

        # Does post request
        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        self.compare_values(
            'There is another equipment with same name VM-SANITY-TEST',
            response.data['detail'])

    def test_post_equipment_invalid_env(self):
        """Test of error to post of one equipment with environment non existent.
        """

        name_file = self.json_path % 'post_one_equipment_invalid_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        self.compare_values(
            'There is no environment with id = 10.',
            response.data['detail'])

    def test_post_equipment_invalid_group(self):
        """Test of error to post of one equipment with group non existent.
        """

        name_file = self.json_path % 'post_one_equipment_invalid_group.json'

        # Does post request
        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        self.compare_values(
            'There is no group with a pk = 10.',
            response.data['detail'])
