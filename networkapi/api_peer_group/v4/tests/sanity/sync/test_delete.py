# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class PeerGroupDeleteSuccessTestCase(NetworkApiTestCase):

    peer_group_uri = '/api/v4/peer-group/'
    fixtures_path = 'networkapi/api_peer_group/v4/fixtures/{}'

    fixtures = [
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
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_environment_peer_group.json'),

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_peer_group(self):
        """Test DELETE PeerGroup."""

        delete_ids = [1]
        uri = mount_url(self.peer_group_uri,
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
            u'PeerGroup id = 1 do not exist',
            response.data['detail']
        )


class PeerGroupDeleteErrorTestCase(NetworkApiTestCase):

    peer_group_uri = '/api/v4/peer-group/'
    fixtures_path = 'networkapi/api_peer_group/v4/fixtures/{}'

    fixtures = [
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

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_inexistent_peer_group(self):
        """Test DELETE inexistent PeerGroup."""

        delete_ids = [1000]
        uri = mount_url(self.peer_group_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'PeerGroup id = 1000 do not exist',
            response.data['detail']
        )

    def test_delete_peer_group_assoc_with_neighbors(self):
        """Test DELETE PeerGroup associated with neighbors."""

        delete_ids = [1]
        uri = mount_url(self.peer_group_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'PeerGroup id = 1 is associated '
            u'with NeighborsV4 id = [1] and NeighborsV6 id = [1]',
            response.data['detail']
        )


class EnvironmentPeerGroupDeleteTestCase(NetworkApiTestCase):

    peer_group_uri = '/api/v4/peer-group/'
    environment_peer_group_uri = '/api/v4/peer-group/1/environment'
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
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
    ]

    json_path = 'api_peer_group/v4/tests/sanity/json/delete/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'

    def test_delete_removes_only_requested_environment_association(self):
        payload_path = self.json_path.format('delete_environment_association.json')
        response = self.client.delete(
            self.environment_peer_group_uri,
            data=self.load_json(payload_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        uri = mount_url(self.peer_group_uri, [1], fields=['id', 'environments'])
        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)
        self.compare_values(
            [2],
            response.data['peer_groups'][0]['environments'])

    def test_delete_rejects_nonexistent_peer_group(self):
        response = self.client.delete(
            '/api/v4/peer-group/1000/environment',
            data=self.load_json(
                self.json_path.format('delete_environment_association.json')),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

    def test_delete_rejects_empty_environments_ids(self):
        response = self.client.delete(
            self.environment_peer_group_uri,
            data='{"environments_ids": []}',
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
