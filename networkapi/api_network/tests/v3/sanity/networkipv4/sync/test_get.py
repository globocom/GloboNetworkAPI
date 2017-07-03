# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url


class NetworkIPv4GetSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/vlan/fixtures/initial_tipo_rede.json',
        'networkapi/filter/fixtures/initial_filter.json',
        'networkapi/filterequiptype/fixtures/initial_filterequiptype.json',
        'networkapi/equipamento/fixtures/initial_tipo_equip.json',
        'networkapi/equipamento/fixtures/initial_equip_marca.json',
        'networkapi/equipamento/fixtures/initial_equip_model.json',

        'networkapi/api_network/fixtures/sanity/initial_config_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_dc.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_ipconfig.json',
        'networkapi/api_network/fixtures/sanity/initial_networkipv4.json',
        'networkapi/api_network/fixtures/sanity/initial_vlan.json',
        'networkapi/api_network/fixtures/sanity/initial_vrf.json',
    ]

    json_path = 'api_network/tests/v3/sanity/networkipv4/json/%s'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_netipv4_by_id_using_basic_kind(self):
        """Test of success to get a Network IPv4 by id using basic kind."""

        name_file = self.json_path % 'get/basic/pk_1.json'

        # Make a GET request
        response = self.client.get(
            '/api/v3/networkv4/1/?kind=basic',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv4_by_id_using_basic_kind(self):
        """Test of success to get two Network IPv4 by id using basic kind."""

        name_file = self.json_path % 'get/basic/pk_1;2.json'

        # Make a GET request
        response = self.client.get(
            '/api/v3/networkv4/1;2/?kind=basic',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_netipv4_by_search_using_basic_kind(self):
        """Test of success to get a Network IPv4 by search using basic kind."""

        name_file = self.json_path % 'get/basic/pk_1.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 10,
                'oct3': 0,
                'oct4': 0
            }]
        }

        get_url = prepare_url('/api/v3/networkv4/',
                              search=search, kind=['basic'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv4_by_search_using_basic_kind(self):
        """Test of success to get two Network IPv4 by search using basic kind."""

        name_file = self.json_path % 'get/basic/pk_1;2.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'broadcast': '10.10.0.255'
            }, {
                'broadcast': '10.10.1.127'
            }]
        }

        get_url = prepare_url('/api/v3/networkv4/',
                              search=search, kind=['basic'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_netipv4_by_id_using_details_kind(self):
        """Test of success to get a Network IPv4 by id using details kind."""

        name_file = self.json_path % 'get/details/pk_1.json'

        # Make a GET request
        response = self.client.get(
            '/api/v3/networkv4/1/?kind=details',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv4_by_id_using_details_kind(self):
        """Test of success to get two Network IPv4 by id using details kind."""

        name_file = self.json_path % 'get/details/pk_1;2.json'

        get_url = '/api/v3/networkv4/1;2/?kind=details'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_netipv4_by_search_using_details_kind(self):
        """Test of success to get a Network IPv4 by search using details kind."""

        name_file = self.json_path % 'get/details/pk_1.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 10,
                'oct3': 0,
                'oct4': 0
            }]
        }

        get_url = prepare_url('/api/v3/networkv4/',
                              search=search, kind=['details'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv4_by_search_using_details_kind(self):
        """Test of success to get two Network IPv4 by search using details kind."""

        name_file = self.json_path % 'get/details/pk_1;2.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'broadcast': '10.10.0.255'
            }, {
                'broadcast': '10.10.1.127'
            }]
        }

        get_url = prepare_url('/api/v3/networkv4/',
                              search=search, kind=['details'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])


class NetworkIPv4GetErrorTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/vlan/fixtures/initial_tipo_rede.json',
        'networkapi/filter/fixtures/initial_filter.json',
        'networkapi/filterequiptype/fixtures/initial_filterequiptype.json',
        'networkapi/equipamento/fixtures/initial_tipo_equip.json',
        'networkapi/equipamento/fixtures/initial_equip_marca.json',
        'networkapi/equipamento/fixtures/initial_equip_model.json',

        'networkapi/api_network/fixtures/sanity/initial_config_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_dc.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_ipconfig.json',
        'networkapi/api_network/fixtures/sanity/initial_networkipv4.json',
        'networkapi/api_network/fixtures/sanity/initial_vlan.json',
        'networkapi/api_network/fixtures/sanity/initial_vrf.json',
    ]

    json_path = 'api_network/tests/v3/sanity/networkipv4/json/%s'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_inexistent_netipv4_by_id(self):
        """Test of error to get a inexistent Network IPv4 by id."""

        # Make a GET request
        response = self.client.get(
            '/api/v3/networkv4/1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv4 with pk = 1000.',
            response.data['detail']
        )

    def test_get_two_inexistent_netipv4_by_id(self):
        """Test of error to get two inexistent Network IPv4 by id."""

        # Make a GET request
        response = self.client.get(
            '/api/v3/networkv4/1000;1001/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv4 with pk = 1000.',
            response.data['detail']
        )

    def test_get_a_existent_and_inexistent_netipv4_by_id(self):
        """Test of error to get a existent and a inexistent Network IPv4 by id."""

        # Make a GET request
        response = self.client.get(
            '/api/v3/networkv4/1;1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv4 with pk = 1000.',
            response.data['detail']
        )

    def test_get_inexistent_netipv4_by_search(self):
        """Test of error to get a inexistent Network IPv4 by search."""

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'broadcast': '172.0.200.255'
            }]
        }

        get_url = prepare_url('/api/v3/networkv4/', search=search)

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_values(0, response.data['total'])
