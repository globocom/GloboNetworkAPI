# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class RouteMapGetSuccessTestCase(NetworkApiTestCase):

    route_map_uri = '/api/v4/route-map/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map/{}'

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_route_map.json'),

    ]

    json_path = 'api_route_map/v4/tests/route_map/sanity/json/get/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.fields = ['id', 'name', 'route_map_entries', 'peer_groups',
                       'created']

    def tearDown(self):
        pass

    def test_get_route_maps_by_ids(self):
        """Test GET RouteMaps without kind by ids."""

        route_maps_path = self.json_path.format('pk_1;2.json')

        get_ids = [1, 2]
        uri = mount_url(self.route_map_uri,
                        get_ids,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(route_maps_path,
                                response.data['route_maps'])

    def test_get_basic_route_maps_by_ids(self):
        """Test GET RouteMaps with kind=basic by ids."""

        route_maps_path = self.json_path.format('pk_1;2_basic.json')

        get_ids = [1, 2]
        uri = mount_url(self.route_map_uri,
                        get_ids,
                        kind=['basic'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(route_maps_path,
                                response.data['route_maps'])

    def test_get_details_route_maps_by_ids(self):
        """Test GET RouteMaps with kind=details by ids."""

        route_maps_path = self.json_path.format('pk_1;2_details.json')

        get_ids = [1, 2]
        uri = mount_url(self.route_map_uri,
                        get_ids,
                        kind=['details'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(route_maps_path,
                                response.data['route_maps'])

    def test_get_basic_route_map_by_search(self):
        """Test GET RouteMap with kind=basic by search."""

        route_maps_path = self.json_path.format('pk_1_basic.json')

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'name': 'test_1'
            }]
        }

        uri = mount_url(self.route_map_uri,
                        kind=['basic'],
                        search=search,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(route_maps_path,
                                response.data['route_maps'])


class RouteMapGetErrorTestCase(NetworkApiTestCase):

    route_map_uri = '/api/v4/route-map/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map/{}'

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_route_map.json'),

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def test_get_inexistent_route_map(self):
        """Test GET inexistent RouteMap by id."""

        get_ids = [1000]
        uri = mount_url(self.route_map_uri,
                        get_ids)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'RouteMap id = 1000 do not exist.',
            response.data['detail']
        )
