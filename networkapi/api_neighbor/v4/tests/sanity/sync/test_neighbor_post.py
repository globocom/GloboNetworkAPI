# -*- coding: utf-8 -*-
import json

from django.test.client import Client
from mock import patch
from mock import Mock
from mock import MagicMock
from random import randint

from networkapi.test.mock import MockPluginBgpGeneric
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url
from networkapi.api_neighbor.v4.tests.sanity.sync.mock_objects import _mock_vrf
from networkapi.api_neighbor.v4.tests.sanity.sync.mock_objects import _mock_asn
from networkapi.api_neighbor.v4.tests.sanity.sync.mock_objects import \
    _mock_equipment

json_path = 'api_neighbor/v4/tests/sanity/sync/json/%s'


class NeighborPostSuccessTestCase(NetworkApiTestCase):
    """Class for Test Neighbor package Success POST cases."""

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

    def test_post_one_neighbor(self):
        """Success Test of POST one Neighbor."""

        name_file = json_path % 'post/one_neighbor.json'

        # Does POST request
        response = self.client.post(
            '/api/v4/neighbor/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v4/neighbor/%s/' % response.data[0]['id']

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['neighbors'][0]['id']
        self.compare_json(name_file, response.data)

    def test_post_two_neighbor(self):
        """Success Test of POST two Neighbor."""

        name_file = json_path % 'post/two_neighbor.json'

        # Does POST request
        response = self.client.post(
            '/api/v4/neighbor/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v4/neighbor/%s;%s/' % (response.data[0]['id'],
                                               response.data[1]['id'])

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['neighbors'][0]['id']
        del response.data['neighbors'][1]['id']

        self.compare_json(name_file, response.data)
        

class NeighborDeploySuccessTestCase(NetworkApiTestCase):

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

    @patch('networkapi.api_vrf.models.Vrf.objects.filter')
    @patch('networkapi.api_as.models.As.objects.filter')
    @patch('networkapi.equipamento.models.Equipamento.objects.filter')
    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_try_deploy_uncreated_neighbor_v4(self, test_patch, eqpt_filter,
                                              asn_filter, vrf_filter):
        """Test of success to deploy an uncreated Neighbor IPv4."""

        mock = MockPluginBgpGeneric()
        test_patch.return_value = mock

        eqpt_filter.return_value = [_mock_equipment()]
        asn_filter.return_value = [_mock_asn()]
        vrf_filter.return_value = [_mock_vrf()]

        response = self.client.post(
            '/api/v4/neighbor/deploy/4/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/neighbor/4/?fields=created',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        created = response.data['neighbors'][0]['created']
        self.compare_values(True, created)

    @patch('networkapi.api_vrf.models.Vrf.objects.filter')
    @patch('networkapi.api_as.models.As.objects.filter')
    @patch('networkapi.equipamento.models.Equipamento.objects.filter')
    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_try_deploy_uncreated_neighbor_v6(self, test_patch, eqpt_filter,
                                              asn_filter, vrf_filter):
        """Test of success to deploy an uncreated Neighbor IPv6."""

        mock = MockPluginBgpGeneric()
        test_patch.return_value = mock

        eqpt_filter.return_value = [_mock_equipment()]
        asn_filter.return_value = [_mock_asn()]
        vrf_filter.return_value = [_mock_vrf()]
        test_patch.return_value = mock

        response = self.client.post(
            '/api/v4/neighbor/deploy/5/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/neighbor/5/?fields=created',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        created = response.data['neighbors'][0]['created']
        self.compare_values(True, created)


class NeighborDeployErrorTestCase(NetworkApiTestCase):

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
    def test_try_deploy_created_neighbor(self, test_patch):
        """Test of error to deploy a created Neighbor."""

        mock = MockPluginBgpGeneric()
        test_patch.return_value = mock

        url_post = '/api/v4/neighbor/deploy/3/'

        response = self.client.post(
            url_post,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)

        self.compare_values(u'Neighbor 3 already created.', 
                            response.data['detail'])

        url_get = '/api/v4/neighbor/3/?fields=created'

        response = self.client.get(
            url_get,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        created = response.data['neighbors'][0]['created']
        self.compare_values(True, created)

