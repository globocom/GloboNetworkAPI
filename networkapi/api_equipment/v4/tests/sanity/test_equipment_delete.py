# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EquipmentDeleteTestCase(NetworkApiTestCase):

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

    def tearDown(self):
        pass

    def test_delete_one_equipment_success(self):
        """V4 Test of success to delete of one equipment."""

        response = self.client.delete(
            '/api/v4/equipment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/equipment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Dont there is a equipament by pk = 1.',
            response.data['detail'])

    def test_delete_one_equipment_with_associated_as(self):
        """V4 Test of success to delete equipment with associates AS."""

        response = self.client.delete(
            '/api/v4/equipment/4/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/equipment/4/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Dont there is a equipament by pk = 4.',
            response.data['detail'])
        
        # Check if AS was also deleted
        response = self.client.get(
            '/api/v4/as/4/',
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'AS 4 do not exist.',
            response.data['detail']
        )


class EquipmentDeleteErrorTestCase(NetworkApiTestCase):

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

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_delete_one_inexistent_equipment(self):
        """V4 Test of error to delete of one inexistent equipment."""

        response = self.client.delete(
            '/api/v4/equipment/10/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Dont there is a equipament by pk = 10.',
            response.data['detail'])

