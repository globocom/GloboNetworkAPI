# -*- coding: utf-8 -*-
import json

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class NeighborV4PostSuccessTestCase(NetworkApiTestCase):

    neighbor_v4_uri = '/api/v4/neighborv4/'
    fixtures_path = 'networkapi/api_neighbor/v4/fixtures/{}'

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

        fixtures_path.format('initial_vrf.json'),
        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_vlan.json'),
        fixtures_path.format('initial_networkipv4.json'),
        fixtures_path.format('initial_ipv4.json'),
        fixtures_path.format('initial_asn.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_equipment.json'),
        fixtures_path.format('initial_asn_equipment.json'),
        fixtures_path.format('initial_ipv4_equipment.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
    ]

    json_path = 'api_neighbor/v4/tests/sanity/json/post/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['local_asn', 'remote_asn', 'local_ip', 'remote_ip',
                       'peer_group', 'virtual_interface', 'created']

    def tearDown(self):
        pass

    def test_post_neighbor_v4(self):
        """Test POST NeighborV4."""

        neighbor_v4_path = self.json_path.\
            format('one_neighbor_v4.json')

        response = self.client.post(
            self.neighbor_v4_uri,
            data=self.load_json(neighbor_v4_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_ids = [data['id'] for data in response.data]
        uri = mount_url(self.neighbor_v4_uri,
                        get_ids,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(neighbor_v4_path,
                          response.data)
