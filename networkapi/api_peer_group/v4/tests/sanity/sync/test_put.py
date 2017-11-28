# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class PeerGroupPutSuccessTestCase(NetworkApiTestCase):

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

        fixtures_path.format('initial_vrf.json'),
        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
    ]

    json_path = 'api_peer_group/v4/tests/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['id', 'name', 'environments']

    def tearDown(self):
        pass

    def test_put_peer_groups(self):
        """Test PUT PeerGroups."""

        peer_groups_path = self.json_path.\
            format('one_peer_group.json')

        response = self.client.put(
            self.peer_group_uri,
            data=self.load_json(peer_groups_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

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


class PeerGroupPutErrorTestCase(NetworkApiTestCase):

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

        fixtures_path.format('initial_vrf.json'),
        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
        fixtures_path.format('initial_asn.json'),
        fixtures_path.format('initial_ipv4.json'),
        fixtures_path.format('initial_ipv6.json'),
        fixtures_path.format('initial_networkipv4.json'),
        fixtures_path.format('initial_networkipv6.json'),
        fixtures_path.format('initial_vlan.json'),
        fixtures_path.format('initial_neighbor_v4.json'),
        fixtures_path.format('initial_neighbor_v6.json'),
    ]

    json_path = 'api_peer_group/v4/tests/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'

    def tearDown(self):
        pass

    def test_put_inexistent_peer_group(self):
        """Test PUT inexistent PeerGroup."""

        peer_group_path = self.json_path.\
            format('inexistent_peer_group.json')

        response = self.client.put(
            self.peer_group_uri,
            data=self.load_json(peer_group_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'PeerGroup id = 1000 do not exist',
            response.data['detail']
        )

    def test_put_peer_group_associated_to_deployed_neighbors(self):
        """Test PUT PeerGroup associated to deployed Neighbors."""

        peer_group_path = self.json_path.\
            format('peer_group_assoc_to_deployed_neighbors.json')

        response = self.client.put(
            self.peer_group_uri,
            data=self.load_json(peer_group_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'PeerGroup id = 1 is associated with deployed '
            u'NeighborsV4 id = [1] and NeighborsV6 id = [1]',
            response.data['detail']
        )
