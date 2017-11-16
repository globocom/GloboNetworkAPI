# -*- coding: utf-8 -*-
import json

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class PeerGroupPostSuccessTestCase(NetworkApiTestCase):

    peer_group_uri = '/api/v4/peer-group/'
    fixtures_path = 'networkapi/api_peer_group/v4/fixtures/{}'

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

        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_route_map.json'),

    ]

    json_path = 'api_peer_group/v4/tests/sanity/json/post/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['name', 'route_map_in', 'route_map_out',
                       'environments']

    def tearDown(self):
        pass

    def test_post_peer_groups(self):
        """Test POST PeerGroups."""

        peer_groups_path = self.json_path.\
            format('two_peer_groups.json')

        response = self.client.post(
            self.peer_group_uri,
            data=self.load_json(peer_groups_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_ids = [data['id'] for data in response.data]
        uri = mount_url(self.peer_group_uri,
                        get_ids,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(peer_groups_path,
                          response.data)
