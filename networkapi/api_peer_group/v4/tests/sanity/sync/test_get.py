# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class PeerGroupGetSuccessTestCase(NetworkApiTestCase):

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

        fixtures_path.format('initial_vrf.json'),
        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_environment_peer_group.json'),
    ]

    json_path = 'api_peer_group/v4/tests/sanity/json/get/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.fields = ['id', 'name', 'route_map_in', 'route_map_out',
                       'environments']

    def tearDown(self):
        pass

    def test_get_basic_peer_group_by_id(self):
        """Test GET PeerGroup with kind=basic by id."""

        peer_groups_path = self.json_path.format('pk_1_basic.json')

        get_ids = [1]
        uri = mount_url(self.peer_group_uri,
                        get_ids,
                        kind=['basic'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(peer_groups_path,
                                response.data['peer_groups'])

    def test_get_details_peer_group_by_id(self):
        """Test GET PeerGroup with kind=details by id."""

        peer_groups_path = self.json_path.format('pk_1_details.json')

        get_ids = [1]
        uri = mount_url(self.peer_group_uri,
                        get_ids,
                        kind=['details'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(peer_groups_path,
                                response.data['peer_groups'])

    def test_get_basic_peer_group_by_search(self):
        """Test GET PeerGroup with kind=basic by search."""

        peer_groups_path = self.json_path.format('pk_1_basic.json')

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'route_map_in': 1
            }]
        }

        uri = mount_url(self.peer_group_uri,
                        kind=['basic'],
                        search=search,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(peer_groups_path,
                                response.data['peer_groups'])


class PeerGroupGetErrorTestCase(NetworkApiTestCase):

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


    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def test_get_inexistent_peer_group(self):
        """Test GET inexistent PeerGroup by id."""

        get_ids = [1000]
        uri = mount_url(self.peer_group_uri,
                        get_ids)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'PeerGroup id = 1000 do not exist',
            response.data['detail']
        )
