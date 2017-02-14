# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentVipTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_one_environment(self):
        """Test Success of get one environment vip."""

        response = self.client.get(
            '/api/v3/environment-vip/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_two_environments_vip(self):
        """Test Success of get two environment vip."""

        response = self.client.get(
            '/api/v3/environment-vip/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    # def test_get_success_list_environments_vip(self):
    #     """
    #     Test Success of environment vip list
    #     """

    #     response = self.client.get(
    #         '/api/v3/environment-vip/',
    #         content_type="application/json",
    #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))

    #     self.assertEqual(
    #         200,
    #         response.status_code,
    #         "Status code should be 200 and was %s" % response.status_code
    #     )

    def test_get_success_list_envvip_step(self):
        """Test Success of environment vip by step."""

        # get finalities
        url = '/api/v3/environment-vip/step/'
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

        # get clients
        url = '{0}?finality={1}'.format(
            url, response.data[0].get('finalidade_txt')
        )
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

        # get environments
        url = '{0}&client={1}'.format(
            url, response.data[0].get('cliente_txt')
        )
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

        # get ambiente_p44_txt
        url = '{0}&environmentp44={1}'.format(
            url, response.data[0].get('ambiente_p44_txt')
        )
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_search_envvip(self):
        """Test Success of options list by environment vip id."""

        search = {
            'extends_search': [{'finalidade_txt': 'test'}],
            'end_record': 50,
            'start_record': 0,
            'searchable_columns': [],
            'asorting_cols': ['-id'],
            'custom_search': None
        }

        response = self.client.get(
            '/api/v3/environment-vip/?search=%s' % search,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_list_options_by_envvip(self):
        """Test Success of options list by environment vip id."""

        response = self.client.get(
            '/api/v3/option-vip/environment-vip/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_list_options_by_envvip_and_type(self):
        """Test Success of options list by environment vip id and type option.
        """

        response = self.client.get(
            '/api/v3/type-option/environment-vip/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

        response = self.client.get(
            '/api/v3/option-vip/environment-vip/1/type-option/{0}/'.format(
                response.data[0]
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_post_one_env_success(self):
        """Test Success of post of one environment vip."""

        name_file = 'api_environment_vip/tests/json/post_one_envvip.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment-vip/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(201, response.status_code,
                         'Status code should be 201 and was %s' %
                         response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Removes property id
        data = response.data
        del data['environments_vip'][0]['id']

        # Tests if data was inserted
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_put_one_env_success(self):
        """Test Success of put of one environment vip."""

        name_file = 'api_environment_vip/tests/json/put_one_envvip.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment-vip/4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment-vip/4/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        data = response.data

        # Tests if data was updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_delete_one_env_success(self):
        """Test success of delete of one environment vip."""

        response = self.client.delete(
            '/api/v3/environment-vip/5/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

        response = self.client.get(
            '/api/v3/environment-vip/5/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            404,
            response.status_code,
            'Status code should be 404 and was %s' % response.status_code
        )

    def test_delete_one_env_inexistent_error(self):
        """Test success of delete of one environment vip."""

        response = self.client.delete(
            '/api/v3/environment-vip/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            404,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_delete_one_env_related_network_error(self):
        """Test of error to delete one environment vip related with network
        ipv4.
        """

        response = self.client.delete(
            '/api/v3/environment-vip/6/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            400,
            response.status_code,
            'Status code should be 400 and was %s' % response.status_code
        )
