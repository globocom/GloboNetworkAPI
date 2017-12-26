# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class NeighborV6PutSuccessTestCase(NetworkApiTestCase):

    neighbor_v6_uri = '/api/v4/neighborv6/'
    fixtures_path = 'networkapi/api_neighbor/v4/fixtures/neighbor_v6/{}'

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
        fixtures_path.format('initial_networkipv6.json'),
        fixtures_path.format('initial_ipv6.json'),
        fixtures_path.format('initial_asn.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_equipment.json'),
        fixtures_path.format('initial_asn_equipment.json'),
        fixtures_path.format('initial_ipv6_equipment.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
        fixtures_path.format('initial_neighbor_v6.json')

    ]

    json_path = 'api_neighbor/v4/tests/neighbor_v6/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['id', 'local_asn', 'remote_asn', 'local_ip',
                       'remote_ip', 'peer_group', 'virtual_interface']

    def tearDown(self):
        pass

    def test_put_neighbor_v6(self):
        """Test PUT NeighborV6."""

        neighbor_v6_path = self.json_path.\
            format('one_neighbor_v6.json')

        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_ids = [data['id'] for data in response.data]
        uri = mount_url(self.neighbor_v6_uri,
                        get_ids,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(neighbor_v6_path,
                          response.data)


class NeighborV6PutErrorTestCase(NetworkApiTestCase):

    neighbor_v6_uri = '/api/v4/neighborv6/'
    fixtures_path = 'networkapi/api_neighbor/v4/fixtures/neighbor_v6/{}'

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
        fixtures_path.format('initial_networkipv6.json'),
        fixtures_path.format('initial_ipv6.json'),
        fixtures_path.format('initial_asn.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_equipment.json'),
        fixtures_path.format('initial_asn_equipment.json'),
        fixtures_path.format('initial_ipv6_equipment.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
        fixtures_path.format('initial_neighbor_v6.json')
    ]

    json_path = 'api_neighbor/v4/tests/neighbor_v6/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'

    def tearDown(self):
        pass

    def test_put_inexistent_neighbor_v6(self):
        """Test PUT inexistent NeighborV6."""

        neighbor_v6_path = self.json_path.\
            format('inexistent_neighbor_v6.json')

        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'NeighborV6 id = 1000 do not exist',
            response.data['detail']
        )

    def test_put_neighbor_v6_in_peer_group_without_permission(self):
        """Test PUT NeighborV6 in peer group without permission."""

        neighbor_v6_path = self.json_path. \
            format('neighbor_v6_in_peer_without_perm.json')

        authorization = self.get_http_authorization('test2')
        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'Peer Group id = 1 does not have permissions '
            u'to be associated with Neighbor',
            response.data['detail']
        )

    def test_put_neighbor_v6_with_local_ip_vrf_not_eq_to_remote_ip_vrf(self):
        """Test PUT NeighborV6 with LocalIp Vrf not equal to RemoteIp Vrf."""

        neighbor_v6_path = self.json_path. \
            format('neighbor_v6_local_ip_vrf_not_eq_remote_ip_vrf.json')

        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'LocalIp id = 5 and RemoteIp id = 6 are in different Vrfs',
            response.data['detail']
        )

    def test_put_neighbor_v6_with_locals_in_different_eqpts(self):
        """Test PUT NeighborV6 with LocalIp and LocalAsn
           in different equipments.
        """

        neighbor_v6_path = self.json_path. \
            format('neighbor_v6_locals_in_different_eqpts.json')

        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'LocalIp id = 6 and LocalAsn id = 5 belongs '
            u'to different Equipments',
            response.data['detail']
        )

    def test_put_neighbor_v6_with_remotes_in_different_eqpts(self):
        """Test PUT NeighborV6 with RemoteIp and RemoteAsn
           in different equipments.
        """

        neighbor_v6_path = self.json_path. \
            format('neighbor_v6_remotes_in_different_eqpts.json')

        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'RemoteIp id = 8 and RemoteAsn id = 7 '
            u'belongs to different Equipments',
            response.data['detail']
        )

    def test_put_neighbor_v6_with_peer_group_envs_diff_local_ip_env(self):
        """Test PUT NeighborV6 with peer groups environments
           different than LocalIp Environment."""

        neighbor_v6_path = self.json_path. \
            format('neighbor_v6_with_peer_group_envs_'
                   'diff_than_local_ip_env.json')

        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'LocalIp id = 1 and PeerGroup id = 3 '
            u'belongs to different Environments',
            response.data['detail']
        )

    def test_put_neighbor_v6_duplicated(self):
        """Test PUT duplicated NeighborV6."""

        neighbor_v6_path = self.json_path. \
            format('neighbor_v6_duplicated.json')

        response = self.client.put(
            self.neighbor_v6_uri,
            data=self.load_json(neighbor_v6_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            u'It already exists Neighbor with LocalAsn id = 1, '
            u'LocalIp id = 1, RemoteAsn id = 2 and RemoteIp id = 2',
            response.data['detail']
        )
