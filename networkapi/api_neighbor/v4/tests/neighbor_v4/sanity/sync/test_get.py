# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class NeighborV4GetSuccessTestCase(NetworkApiTestCase):

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
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_equipment.json'),
        fixtures_path.format('initial_asn_equipment.json'),
        fixtures_path.format('initial_ipv4_equipment.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
        fixtures_path.format('initial_neighbor_v4.json')
    ]

    json_path = 'api_neighbor/v4/tests/neighbor_v4/sanity/json/get/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.fields = ['id', 'local_asn', 'remote_asn', 'local_ip',
                       'remote_ip', 'peer_group', 'virtual_interface',
                       'created']

    def tearDown(self):
        pass

    def test_get_basic_neighbor_v4_by_ids(self):
        """Test GET NeighborV4 with kind=basic by ids."""

        neighbor_v4_path = self.json_path.format('pk_1_basic.json')

        get_ids = [1]
        uri = mount_url(self.neighbor_v4_uri,
                        get_ids,
                        kind=['basic'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(neighbor_v4_path,
                                response.data['neighbors'])

    def test_get_details_neighbor_v4_by_ids(self):
        """Test GET NeighborV4 with kind=details by ids."""

        neighbor_v4_path = self.json_path.format('pk_1_details.json')

        get_ids = [1]
        uri = mount_url(self.neighbor_v4_uri,
                        get_ids,
                        kind=['details'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(neighbor_v4_path,
                                response.data['neighbors'])

    def test_get_basic_neighbor_v4_by_search(self):
        """Test GET NeighborV4 with kind=basic by search."""

        neighbor_v4_path = self.json_path.format('pk_1_basic.json')

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'virtual_interface': 'test_vi'
            }]
        }

        uri = mount_url(self.neighbor_v4_uri,
                        kind=['basic'],
                        search=search,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(neighbor_v4_path,
                                response.data['neighbors'])


class NeighborV4GetErrorTestCase(NetworkApiTestCase):

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


    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def test_get_inexistent_neighbor_v4(self):
        """Test GET inexistent NeighborV4 by id."""

        get_ids = [1000]
        uri = mount_url(self.neighbor_v4_uri,
                        get_ids)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'NeighborV4 id = 1000 do not exist',
            response.data['detail']
        )
