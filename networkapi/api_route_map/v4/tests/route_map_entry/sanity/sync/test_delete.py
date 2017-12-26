# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class RouteMapEntryDeleteSuccessTestCase(NetworkApiTestCase):

    route_map_entry_uri = '/api/v4/route-map-entry/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map_entry/{}'

    fixtures = [
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

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_route_map_entry(self):
        """Test DELETE RouteMapEntry."""

        delete_ids = [1]
        uri = mount_url(self.route_map_entry_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'RouteMapEntry id = 1 do not exist',
            response.data['detail']
        )


class RouteMapEntryDeleteErrorTestCase(NetworkApiTestCase):

    route_map_entry_uri = '/api/v4/route-map-entry/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map_entry/{}'

    fixtures = [
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
        fixtures_path.format('initial_asn.json'),
        fixtures_path.format('initial_vrf.json'),
        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_vlan.json'),
        fixtures_path.format('initial_networkipv4.json'),
        fixtures_path.format('initial_ipv4.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_neighbor_v4.json'),
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_inexistent_route_map_entries(self):
        """Test DELETE inexistent RouteMapEntries."""

        delete_ids = [1000, 1001]
        uri = mount_url(self.route_map_entry_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'RouteMapEntry id = 1000 do not exist',
            response.data['detail']
        )

    def test_delete_route_map_entry_with_deployed_route_map(self):
        """Test DELETE RouteMapEntry with deployed RouteMap."""

        delete_ids = [2]
        uri = mount_url(self.route_map_entry_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'RouteMap id = 2 is deployed at '
            u'NeighborsV4 = [1] and NeighborsV6 = []',
            response.data['detail']
        )
