# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

import operator

json_path = 'api_neighbor/v4/tests/sanity/sync/json/%s'

class NeighborGetSuccessTestCase(NetworkApiTestCase):
    """Class for Test Neighbor package Success GET cases."""

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

    def test_get_one_basic_neighbor(self):
        """Success Test of GET one Basic Neighbor."""

        name_file = json_path % 'get/basic/pk_1.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/neighbor/1/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['neighbors'])

    def test_get_two_basic_neighbor(self):
        """Success Test of GET two Basic Neighbor."""

        name_file = json_path % 'get/basic/pk_1;2.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/neighbor/1;2/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['neighbors'])

    def test_get_one_neighbor_with_virtual_interface_details(self):
        """Success Test of GET one Neighbor with Virtual Interface details."""

        name_file = json_path % 'get/details/pk_1_virtual_interface.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/neighbor/1/?include=virtual_interface__details',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['neighbors'])

    def test_get_two_basic_neighbor_by_search(self):
        """Success Test of GET two basic Neighbor by search."""

        name_file = json_path % 'get/basic/pk_1;2.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'virtual_interface__id__in': [1],
            }]
        }

        get_url = prepare_url('/api/v4/neighbor/', search=search)

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response.data['neighbors'].sort(key=operator.itemgetter('id'))

        self.compare_json_lists(name_file, response.data['neighbors'])


class NeighborGetErrorTestCase(NetworkApiTestCase):
    """Class for Test Neighbor package Error GET cases."""

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

    def test_get_one_inexistent_neighbor(self):
        """Error Test of GET one inexistent Neighbor."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/neighbor/1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Neighbor 1000 do not exist.',
            response.data['detail']
        )

    def test_get_two_inexistent_neighbor(self):
        """Error Test of GET two inexistent Neighbor."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/neighbor/1000;1001/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Neighbor 1000 do not exist.',
            response.data['detail']
        )

    def test_get_one_existent_and_one_inexistent(self):
        """Error Test of GET one existent and one inexistent Neighbor."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/neighbor/1;1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Neighbor 1000 do not exist.',
            response.data['detail']
        )

