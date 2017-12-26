# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

json_path = 'api_asn/v4/tests/sanity/sync/json/%s'


class AsDeleteSuccessTestCase(NetworkApiTestCase):
    """Class for Test AS package Success DELETE cases."""

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

    def test_delete_one_as(self):
        """Success Test of DELETE one AS."""

        response = self.client.delete(
            '/api/v4/as/3/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/as/3/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'ASN 3 do not exist.',
            response.data['detail']
        )

    def test_delete_two_as(self):
        """Success Test of DELETE two AS."""

        response = self.client.delete(
            '/api/v4/as/3;4/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        for id_ in xrange(3, 4 + 1):
            response = self.client.get(
                '/api/v4/as/%s/' % id_,
                HTTP_AUTHORIZATION=self.authorization
            )

            self.compare_status(404, response.status_code)

            self.compare_values(
                u'ASN %s do not exist.' % id_,
                response.data['detail']
            )


class AsDeleteErrorTestCase(NetworkApiTestCase):
    """Class for Test AS package Error DELETE cases."""

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

    def test_delete_one_as_with_equipments(self):
        """Error Test of DELETE one AS that is related to two Equipments."""

        delete_url = '/api/v4/as/1/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)

        self.compare_values(
            u'Cannot delete ASN 1 because it is associated '
            u'with Equipments [1, 2].',
            response.data['detail']
        )

    def test_delete_one_inexistent_as(self):
        """Error Test of DELETE one inexistent AS."""

        delete_url = '/api/v4/as/1000/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'ASN 1000 do not exist.',
            response.data['detail']
        )

    def test_delete_one_as_with_equipments_and_one_as_without_equipments(self):
        """Error Test of DELETE one AS that is related to two Equipments
            and AS that is not related with Equipments.
        """

        delete_url = '/api/v4/as/1;3/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)

        self.compare_values(
            u'Cannot delete ASN 1 because it is associated '
            u'with Equipments [1, 2].',
            response.data['detail']
        )

        # Check if AS 3 not changed
        response = self.client.get(
            '/api/v4/as/3/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        name_file = json_path % 'get/basic/pk_3.json'

        self.compare_json_lists(name_file, response.data['asns'])
