import json
import logging
import sys
from itertools import izip
from time import time

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

        'networkapi/api_network/fixtures/initial_environment_dc.json',
        'networkapi/api_network/fixtures/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/initial_environment_gl3.json',
        verbosity=1
    )

# TODO: Lembrar de fazer alguns testes relativos à fields específicos

class NetworkIPv4GetTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_netipv4_by_id_using_basic_kind(self):
        """Tries to get a Network IPv4 by id using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        get_url = '/api/v3/networkv4/1/?kind=basic'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)

    def test_get_two_netipv4_by_ids_using_basic_kind(self):
        """Tries to get two Network IPv4 by ids using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        get_url = '/api/v3/networkv4/1;2/?kind=basic'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)

    def test_get_netipv4_by_search_using_basic_kind(self):
        """Tries to get a Network IPv4 by search using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        search = {}

        get_url = prepare_url('/api/v3/networkv4/', search=search, kind=['basic'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)

    def test_get_two_netipv4_by_search_using_basic_kind(self):
        """Tries to get two Network IPv4 by search using 'basic' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        search = {}

        get_url = prepare_url('/api/v3/networkv4/', search=search, kind=['basic'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)

    def test_get_netipv4_by_id_using_details_kind(self):
        """Tries to get a Network IPv4 by id using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        get_url = '/api/v3/networkv4/1/?kind=details'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)

    def test_get_two_netipv4_by_ids_using_details_kind(self):
        """Tries to get two Network IPv4 by ids using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        get_url = '/api/v3/networkv4/1;2/?kind=details'

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)

    def test_get_netipv4_by_search_using_details_kind(self):
        """Tries to get a Network IPv4 by search using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        search = {}

        get_url = prepare_url('/api/v3/networkv4/', search=search, kind=['details'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)

    def test_get_two_netipv4_by_search_using_details_kind(self):
        """Tries to get two Network IPv4 by search using 'details' kind."""

        name_file = 'api_network/tests/v3/sanity/json/'

        search = {}

        get_url = prepare_url('/api/v3/networkv4/', search=search, kind=['details'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(name_file, response.data)


