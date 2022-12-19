# -*- coding: utf-8 -*-
import logging

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class EnvironmentVipGetTestCase(NetworkApiTestCase):

    fixtures = [

        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/api_environment_vip/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_get_success_one_environment(self):
        """Test of success to get one environment vip."""

        response = self.client.get(
            '/api/v3/environment-vip/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_two_environments_vip(self):
        """Test of success to get two environment vip."""

        response = self.client.get(
            '/api/v3/environment-vip/1;2/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_list_envvip_step(self):
        """Test of success to get environment vip by step."""

        # get finalities
        url = '/api/v3/environment-vip/step/'
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # get clients
        url = '{0}?finality={1}'.format(
            url, response.data[0].get('finalidade_txt')
        )
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # get environments
        url = '{0}&client={1}'.format(
            url, response.data[0].get('cliente_txt')
        )
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

        # get ambiente_p44_txt
        url = '{0}&environmentp44={1}'.format(
            url, response.data[0].get('ambiente_p44_txt')
        )
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_search_envvip(self):
        """Test of success to get options list by environment vip id."""

        search = {
            'extends_search': [{'finalidade_txt': 'SANITY-TEST'}],
            'end_record': 50,
            'start_record': 0,
            'searchable_columns': [],
            'asorting_cols': ['-id'],
            'custom_search': None
        }

        response = self.client.get(
            '/api/v3/environment-vip/?search=%s' % search,
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_list_options_by_envvip(self):
        """Test of success to get options list by environment vip id."""

        response = self.client.get(
            '/api/v3/option-vip/environment-vip/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_list_options_by_envvip_and_type(self):
        """Test of success to get options list by environment vip id and type option.
        """

        response = self.client.get(
            '/api/v3/type-option/environment-vip/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v3/option-vip/environment-vip/1/type-option/{0}/'.format(
                response.data[0]
            ),
            content_type='application/json')

        self.compare_status(200, response.status_code)
