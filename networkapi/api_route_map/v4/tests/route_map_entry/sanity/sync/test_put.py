# -*- coding: utf-8 -*-
import json

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class RouteMapEntryPutSuccessTestCase(NetworkApiTestCase):

    route_map_entry_uri = '/api/v4/route-map-entry/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map_entry/{}'

    fixtures = [
        'networkapi/config/fixtures/initial_config.json',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_list_config_bgp.json'),
        fixtures_path.format('initial_route_map_entry.json'),
    ]

    json_path = 'api_route_map/v4/tests/route_map_entry/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['id', 'action', 'action_reconfig', 'order',
                       'list_config_bgp', 'route_map']

    def tearDown(self):
        pass

    def test_put_route_map_entries(self):
        """Test PUT RouteMapEntries."""

        route_map_entries_path = self.json_path.\
            format('two_route_map_entries.json')

        response = self.client.put(
            self.route_map_entry_uri,
            data=self.load_json(route_map_entries_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_ids = [data['id'] for data in response.data]
        uri = mount_url(self.route_map_entry_uri,
                        get_ids,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(route_map_entries_path,
                          response.data)


class RouteMapEntryPutErrorTestCase(NetworkApiTestCase):

    route_map_entry_uri = '/api/v4/route-map-entry/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map_entry/{}'

    fixtures = [
        'networkapi/config/fixtures/initial_config.json',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_list_config_bgp.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_route_map_entry.json'),

    ]

    json_path = 'api_route_map/v4/tests/route_map_entry/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'

    def tearDown(self):
        pass

    def test_put_inexistent_route_map_entry(self):
        """Test PUT inexistent RouteMapEntry."""

        route_map_entry_path = self.json_path.\
            format('inexistent_route_map_entry.json')

        response = self.client.put(
            self.route_map_entry_uri,
            data=self.load_json(route_map_entry_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'RouteMapEntry id = 3 do not exist.',
            response.data['detail']
        )

    def test_put_duplicated_route_map_entry(self):
        """Test PUT duplicated RouteMapEntry."""

        route_map_entry_path = self.json_path.\
            format('duplicated_route_map_entry.json')

        response = self.client.put(
            self.route_map_entry_uri,
            data=self.load_json(route_map_entry_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'It already exists RouteMapEntry with ListConfigBGP '
            u'id = 2 and RouteMap id = 2.',
            response.data['detail']
        )
