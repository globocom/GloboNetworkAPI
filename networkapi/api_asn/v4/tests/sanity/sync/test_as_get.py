# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_asn/v4/tests/sanity/sync/json/%s'

class AsGetSuccessTestCase(NetworkApiTestCase):
    """Class for Test AS package Success GET cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_asn/v4/fixtures/initial_asn.json',
        'networkapi/api_asn/v4/fixtures/initial_equipment.json',
        'networkapi/api_asn/v4/fixtures/initial_asnequipment.json'

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_one_basic_as(self):
        """Success Test of GET one Basic AS."""

        name_file = json_path % 'get/basic/pk_1.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/as/1/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['asns'])

    def test_get_two_basic_as(self):
        """Success Test of GET two Basic AS."""

        name_file = json_path % 'get/basic/pk_1;2.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/as/1;2/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['asns'])

    def test_get_one_as_with_equipments_ids(self):
        """Success Test of GET one AS with two Equipments ids."""

        name_file = json_path % 'get/basic/pk_1_eqpts.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/as/1/?include=equipments',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['asns'])

    def test_get_one_as_with_equipments_details(self):
        """Success Test of GET one AS with Equipments details."""

        name_file = json_path % 'get/details/pk_1_eqpts.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/as/1/?include=equipments__details',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['asns'])

    def test_get_two_basic_as_by_search(self):
        """Success Test of GET two basic AS."""

        name_file = json_path % 'get/basic/pk_1;2.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'asnequipment__equipment__in': [1,2,3,4],
            }]
        }

        get_url = prepare_url('/api/v4/as/',
                              search=search, kind=['basic'],
                              exclude=['equipments'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['asns'])


class AsGetErrorTestCase(NetworkApiTestCase):
    """Class for Test AS package Error GET cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_asn/v4/fixtures/initial_asn.json',
        'networkapi/api_asn/v4/fixtures/initial_equipment.json',
        'networkapi/api_asn/v4/fixtures/initial_asnequipment.json'

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_one_inexistent_as(self):
        """Error Test of GET one inexistent AS."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/as/1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'ASN 1000 do not exist.',
            response.data['detail']
        )

    def test_get_two_inexistent_as(self):
        """Error Test of GET two inexistent AS."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/as/1000;1001/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'ASN 1000 do not exist.',
            response.data['detail']
        )

    def test_get_one_existent_and_one_inexistent(self):
        """Error Test of GET one existent and one inexistent AS."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/as/1;1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'ASN 1000 do not exist.',
            response.data['detail']
        )

