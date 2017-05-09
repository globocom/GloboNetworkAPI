# -*- coding: utf-8 -*-
import logging

from django.core.management import call_command
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


def setup():
    call_command(
        'loaddata',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/api_pools/fixtures/initial_optionspool.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/healthcheckexpect/fixtures/initial_healthcheck.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_pools/fixtures/initial_base.json',
        'networkapi/api_pools/fixtures/initial_pools_1.json',
        verbosity=0
    )


class PoolGetTestCase(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_pool_list_details_success(self):
        """Test Success of pool list(details)."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_list_details.json'

        response = self.client.get(
            '/api/v3/pool/details/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data.get('server_pools'))

    def test_get_one_pool_details_success(self):
        """Test Success of one pool(details)."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_ids_1_details.json'

        response = self.client.get(
            '/api/v3/pool/details/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_two_pool_kind_details_success(self):
        """Test Success of two pools with kind details."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_ids_1_2_details.json'

        response = self.client.get(
            '/api/v3/pool/1;2/?kind=details',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_two_pool_details_success(self):
        """Test Success of two pools(details)."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_ids_1_2_details.json'

        response = self.client.get(
            '/api/v3/pool/details/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_pool_list_success(self):
        """Test Success of pool list."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_list.json'

        response = self.client.get(
            '/api/v3/pool/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data.get('server_pools'))

    def test_get_one_pool_success(self):
        """Test Success of one pool."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_ids_1.json'

        response = self.client.get(
            '/api/v3/pool/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_two_pool_success(self):
        """Test Success of two pools."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_ids_1_2.json'

        response = self.client.get(
            '/api/v3/pool/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_pool_list_by_envvip_success(self):
        """Test Success of pool by environment vip."""

        name_file = 'api_pools/tests/sanity/json/get/test_get_pool_envvip_1.json'

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/environment-vip/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_option_pool_list_by_envvip_success(self):
        """Test Success of pool by environment vip."""

        # try to get datas
        response = self.client.get(
            '/api/v3/option-pool/environment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
