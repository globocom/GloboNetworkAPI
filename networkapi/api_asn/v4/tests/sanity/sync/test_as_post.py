# -*- coding: utf-8 -*-
import json

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

json_path = 'api_asn/v4/tests/sanity/sync/json/%s'


class AsPostSuccessTestCase(NetworkApiTestCase):
    """Class for Test AS package Success POST cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_asn/v4/fixtures/initial_asn.json',
        'networkapi/api_asn/v4/fixtures/initial_equipment.json',
        'networkapi/api_asn/v4/fixtures/initial_asnequipment.json'

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_post_one_as(self):
        """Success Test of POST one AS."""

        name_file = json_path % 'post/one_as.json'

        # Does POST request
        response = self.client.post(
            '/api/v4/as/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v4/as/%s/?kind=basic&exclude=equipments' % \
                  response.data[0]['id']

        name_file_get = json_path % 'get/basic/pk_1.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        response.data['asns'][0]['id'] = 1
        self.compare_json(name_file_get, response.data['asns'])

    def test_post_two_as(self):
        """Success Test of POST two AS."""

        name_file = json_path % 'post/two_as.json'

        # Does POST request
        response = self.client.post(
            '/api/v4/as/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v4/as/%s;%s/?kind=basic&exclude=equipments' \
                  % (response.data[0]['id'], response.data[1]['id'])

        name_file_get = json_path % 'get/basic/pk_1;2.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        response.data['asns'][0]['id'] = 1
        response.data['asns'][1]['id'] = 2

        self.compare_json(name_file_get, response.data['asns'])
