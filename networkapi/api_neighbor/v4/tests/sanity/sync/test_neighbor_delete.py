# -*- coding: utf-8 -*-
from django.test.client import Client
from mock import patch

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url
from networkapi.test.mock import MockPluginBgp

json_path = 'api_neighbor/v4/tests/sanity/sync/json/%s'


class NeighborDeleteSuccessTestCase(NetworkApiTestCase):
    """Class for Test Neighbor package Success DELETE cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        
        'networkapi/api_neighbor/v4/fixtures/initial_vrf.json',
        'networkapi/api_neighbor/v4/fixtures/initial_virtual_interface.json',
        'networkapi/api_neighbor/v4/fixtures/initial_neighbor.json',    
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_one_neighbor(self):
        """Success Test of DELETE one Neighbor."""

        response = self.client.delete(
            '/api/v4/neighbor/1/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/neighbor/1/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Neighbor 1 do not exist.',
            response.data['detail']
        )

    def test_delete_two_neighbor(self):
        """Success Test of DELETE two Neighbor."""

        response = self.client.delete(
            '/api/v4/neighbor/1;2/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        for id_ in xrange(1, 2+1):
            response = self.client.get(
                '/api/v4/neighbor/%s/' % id_,
                HTTP_AUTHORIZATION=self.authorization
            )

            self.compare_status(404, response.status_code)

            self.compare_values(
                u'Neighbor %s do not exist.' % id_,
                response.data['detail']
            )


class NeighborDeleteErrorTestCase(NetworkApiTestCase):
    """Class for Test Neighbor package Error DELETE cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        
        'networkapi/api_neighbor/v4/fixtures/initial_vrf.json',
        'networkapi/api_neighbor/v4/fixtures/initial_virtual_interface.json',
        'networkapi/api_neighbor/v4/fixtures/initial_neighbor.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_one_inexistent_neighbor(self):
        """Error Test of DELETE one inexistent Neighbor."""

        delete_url = '/api/v4/neighbor/1000/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Neighbor 1000 do not exist.',
            response.data['detail']
        )


class NeighborUnDeploySuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_neighbor/v4/fixtures/initial_vrf.json',
        'networkapi/api_neighbor/v4/fixtures/initial_virtual_interface.json',
        'networkapi/api_neighbor/v4/fixtures/initial_neighbor.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_try_undeploy_neighbor(self, test_patch):
        """Test of success to undeploy a Neighbor."""

        mock = MockPluginBgp()
        mock.status(True)
        test_patch.return_value = mock

        response = self.client.delete(
            '/api/v4/neighbor/deploy/3/',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/neighbor/3/?fields=created',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        created = response.data['neighbors'][0]['created']
        self.compare_values(False, created)
        

class NeighborUnDeployErrorTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_neighbor/v4/fixtures/initial_vrf.json',
        'networkapi/api_neighbor/v4/fixtures/initial_virtual_interface.json',
        'networkapi/api_neighbor/v4/fixtures/initial_neighbor.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_try_undeploy_non_deployed_neighbor(self, test_patch):
        """Test of error to undeploy a non deployed Neighbor."""

        mock = MockPluginBgp()
        mock.status(False)
        test_patch.return_value = mock

        response = self.client.delete(
            '/api/v4/neighbor/deploy/1/',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)

        self.compare_values(u'Neighbor 1 not created.',
                            response.data['detail'])

        response = self.client.get(
            '/api/v4/neighbor/1/?fields=created',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        created = response.data['neighbors'][0]['created']
        self.compare_values(False, created)
