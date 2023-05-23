# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class NeighborV4DeleteSuccessTestCase(NetworkApiTestCase):

    neighbor_v4_uri = '/api/v4/neighborv4/'
    fixtures_path = 'networkapi/api_neighbor/v4/fixtures/neighbor_v4/{}'

    fixtures = [
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
        fixtures_path.format('initial_equipment.json'),
        fixtures_path.format('initial_asn_equipment.json'),
        fixtures_path.format('initial_ipv4_equipment.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
        fixtures_path.format('initial_neighbor_v4.json')
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_neighbor_v4(self):
        """Test DELETE NeighborV4."""

        delete_ids = [1]
        uri = mount_url(self.neighbor_v4_uri,
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
            u'NeighborV4 id = 1 do not exist',
            response.data['detail']
        )


class NeighborV4DeleteErrorTestCase(NetworkApiTestCase):

    neighbor_v4_uri = '/api/v4/neighborv4/'
    fixtures_path = 'networkapi/api_neighbor/v4/fixtures/neighbor_v4/{}'

    fixtures = [
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
        fixtures_path.format('initial_neighbor_v4.json')
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_inexistent_neighbors_v4(self):
        """Test DELETE inexistent NeighborsV4."""

        delete_ids = [1000, 1001]
        uri = mount_url(self.neighbor_v4_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'NeighborV4 id = 1000 do not exist',
            response.data['detail']
        )

    def test_delete_deployed_neighbor_v4(self):
        """Test DELETE deployed NeighborV4."""

        delete_ids = [2]
        uri = mount_url(self.neighbor_v4_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'NeighborV4 id = 2 is deployed',
            response.data['detail']
        )
