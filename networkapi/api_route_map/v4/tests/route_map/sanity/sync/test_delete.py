# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class RouteMapDeleteSuccessTestCase(NetworkApiTestCase):

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

    def tearDown(self):
        pass

    def test_delete_route_maps(self):
        """Test DELETE RouteMaps."""

        delete_ids = [1, 2]
        uri = mount_url(self.route_map_uri,
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
            u'RouteMap id = 1 do not exist.',
            response.data['detail']
        )


class RouteMapDeleteErrorTestCase(NetworkApiTestCase):

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

    def tearDown(self):
        pass

    def test_delete_inexistent_route_maps(self):
        """Test DELETE inexistent RouteMaps."""

        delete_ids = [3, 4]
        uri = mount_url(self.route_map_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'RouteMap id = 3 do not exist.',
            response.data['detail']
        )
