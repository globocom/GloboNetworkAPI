# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class ListConfigBGPGetSuccessTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'
    fixtures_path = 'networkapi/api_list_config_bgp/v4/fixtures/{}'

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

    ]

    json_path = 'api_list_config_bgp/v4/tests/sanity/json/get/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.fields = ['id', 'name', 'route_map_entries', 'type', 'config']

    def tearDown(self):
        pass

    def test_get_lists_config_bgp_by_ids(self):
        """Test GET ListsConfigBGP without kind by ids."""

        lists_config_bgp_path = self.json_path.format('pk_1;2.json')

        get_ids = [1, 2]
        uri = mount_url(self.list_config_bgp_uri,
                        get_ids,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(lists_config_bgp_path,
                                response.data['lists_config_bgp'])

    def test_get_basic_lists_config_bgp_by_ids(self):
        """Test GET ListsConfigBGP with kind=basic by ids."""

        lists_config_bgp_path = self.json_path.format('pk_1;2_basic.json')

        get_ids = [1, 2]
        uri = mount_url(self.list_config_bgp_uri,
                        get_ids,
                        kind=['basic'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(lists_config_bgp_path,
                                response.data['lists_config_bgp'])

    def test_get_details_lists_config_bgp_by_ids(self):
        """Test GET ListsConfigBGP with kind=details by ids."""

        lists_config_bgp_path = self.json_path.format('pk_1;2_details.json')

        get_ids = [1, 2]
        uri = mount_url(self.list_config_bgp_uri,
                        get_ids,
                        kind=['details'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(lists_config_bgp_path,
                                response.data['lists_config_bgp'])

    def test_get_basic_list_config_bgp_by_search(self):
        """Test GET ListConfigBGP with kind=basic by search."""

        lists_config_bgp_path = self.json_path.format('pk_1_basic.json')

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'name': 'test_1'
            }]
        }

        uri = mount_url(self.list_config_bgp_uri,
                        kind=['basic'],
                        search=search,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(lists_config_bgp_path,
                                response.data['lists_config_bgp'])


class ListConfigBGPGetErrorTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'
    fixtures_path = 'networkapi/api_list_config_bgp/v4/fixtures/{}'

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

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def test_get_inexistent_list_config_bgp(self):
        """Test GET inexistent ListConfigBGP by id."""

        get_ids = [1000]
        uri = mount_url(self.list_config_bgp_uri,
                        get_ids)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'ListConfigBGP id = 1000 do not exist',
            response.data['detail']
        )
