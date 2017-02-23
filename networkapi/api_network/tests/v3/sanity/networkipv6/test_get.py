# -*- coding: utf-8 -*-
import logging
import sys

from django.core.management import call_command
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

log = logging.getLogger()
log.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
log.addHandler(stream_handler)


def setup():
    call_command(
        'loaddata',
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
        'networkapi/api_network/fixtures/sanity/initial_networkipv6.json',
        'networkapi/api_network/fixtures/sanity/initial_vlan.json',
        'networkapi/api_network/fixtures/sanity/initial_vrf.json',
        verbosity=1
    )


# TODO: Lembrar de fazer alguns testes relativos a fields especificos

class NetworkIPv6GetTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_netipv6_by_id_using_basic_kind(self):
        """Tries to get a Network IPv6 by id using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/basic/pk_1.json'

        get_url = '/api/v3/networkv6/1/?kind=basic'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv6_by_id_using_basic_kind(self):
        """Tries to get two Network IPv6 by id using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/basic/pk_1;2.json'

        get_url = '/api/v3/networkv6/1;2/?kind=basic'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_netipv6_by_search_using_basic_kind(self):
        """Tries to get a Network IPv6 by search using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/basic/pk_1.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [
                {
                    'block1': 'fc00',
                    'block2': '0000',
                    'block3': '0000',
                    'block4': '0000'
                }
            ]
        }

        get_url = prepare_url('/api/v3/networkv6/',
                              search=search, kind=['basic'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv6_by_search_using_basic_kind(self):
        """Tries to get two Network IPv6 by search using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/basic/pk_1;2.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block4': '0000'
            }, {
                'block4': '0001'
            }]
        }

        get_url = prepare_url('/api/v3/networkv6/',
                              search=search, kind=['basic'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_netipv6_by_id_using_details_kind(self):
        """Tries to get a Network IPv6 by id using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/details/pk_1.json'

        get_url = '/api/v3/networkv6/1/?kind=details'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv6_by_id_using_details_kind(self):
        """Tries to get two Network IPv6 by id using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/details/pk_1;2.json'

        get_url = '/api/v3/networkv6/1;2/?kind=details'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_netipv6_by_search_using_details_kind(self):
        """Tries to get a Network IPv6 by search using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/details/pk_1.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0000'
            }]
        }

        get_url = prepare_url('/api/v3/networkv6/',
                              search=search, kind=['details'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_two_netipv6_by_search_using_details_kind(self):
        """Tries to get two Network IPv6 by search using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/details/pk_1;2.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block4': '0000'
            }, {
                'block4': '0001'
            }]
        }

        get_url = prepare_url('/api/v3/networkv6/',
                              search=search, kind=['details'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json_lists(name_file, response.data['networks'])

    def test_get_non_existent_netipv6_by_id(self):
        """Tries to get a non existent Network IPv6 by id."""

        get_url = '/api/v3/networkv6/1000/'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv6 with pk = 1000.',
            response.data['detail']
        )

    def test_get_two_non_existent_netipv6_by_id(self):
        """Tries to get two non existent Network IPv6 by id."""

        get_url = '/api/v3/networkv6/1000;1001/'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv6 with pk = 1000.',
            response.data['detail']
        )

    def test_get_a_existent_and_non_existent_netipv6_by_id(self):
        """Tries to get a existent and a non existent Network IPv6 by id."""

        get_url = '/api/v3/networkv6/1;1000/'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv6 with pk = 1000.',
            response.data['detail']
        )

    def test_get_non_existent_netipv6_by_search(self):
        """Tries to get a non existent Network IPv6 by search."""

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/empty.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'ffff'
            }]
        }

        get_url = prepare_url('/api/v3/networkv6/', search=search)

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['networks'])
