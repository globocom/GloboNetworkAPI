# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url
import json

json_path = 'api_neighbor/v4/tests/sanity/sync/json/%s'


class NeighborPutSuccessTestCase(NetworkApiTestCase):
    """Class for Test Neighbor package Success PUT cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_neighbor/v4/fixtures/initial_vrf.json',
        'networkapi/api_neighbor/v4/fixtures/initial_virtual_interface.json',
        'networkapi/api_neighbor/v4/fixtures/initial_neighbor.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_put_one_neighbor(self):
        """Success Test of PUT one Neighbor."""

        name_file = json_path % 'put/one_neighbor.json'

        # Does PUT request
        response = self.client.put(
            '/api/v4/neighbor/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v4/neighbor/1/'

        name_file_get = json_path % 'get/basic/pk_1_updated.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file_get, response.data['neighbors'])

    def test_put_two_neighbor(self):
        """Success Test of PUT two Neighbor."""

        name_file = json_path % 'put/two_neighbor.json'

        # Does PUT request
        response = self.client.put(
            '/api/v4/neighbor/1;2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v4/neighbor/1;2/'

        name_file_get = json_path % 'get/basic/pk_1;2_updated.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file_get, response.data['neighbors'])


class NeighborPutErrorTestCase(NetworkApiTestCase):
    """Class for Test Neighbor package Error PUT cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_neighbor/v4/fixtures/initial_vrf.json',
        'networkapi/api_neighbor/v4/fixtures/initial_virtual_interface.json',
        'networkapi/api_neighbor/v4/fixtures/initial_neighbor.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_put_one_inexistent_neighbor(self):
        """Error Test of PUT one inexistent Neighbor."""

        name_file = json_path % 'put/inexistent_neighbor.json'

        response = self.client.put(
            '/api/v4/neighbor/1000/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Neighbor 1000 do not exist.',
            response.data['detail']
        )
