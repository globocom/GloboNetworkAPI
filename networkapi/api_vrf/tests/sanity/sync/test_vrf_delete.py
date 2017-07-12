# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_as/v4/tests/sanity/sync/json/%s'

class VrfDeleteErrorTestCase(NetworkApiTestCase):
    """Class for Test Vrf package Error DELETE cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_vrf/fixtures/initial_vrf.json',
        'networkapi/api_vrf/fixtures/initial_virtual_interface.json',

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_one_vrf_associated_to_virtual_interfaces(self):
        """Error Test of DELETE one VRF associated to two Virtual Interfaces."""

        delete_url = '/api/v3/vrf/2/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(500, response.status_code)

        self.compare_values(
            u'Vrf with pk = 2 is associated to Virtual Interfaces [1, 2].',
            response.data['detail']
        )