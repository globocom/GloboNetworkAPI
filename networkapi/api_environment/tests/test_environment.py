# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_one_environment(self):
        """Test of success for get one environment."""

        response = self.client.get(
            '/api/v3/environment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_two_environments(self):
        """Test of success for get two environment."""

        response = self.client.get(
            '/api/v3/environment/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_list_environments(self):
        """Test of success of the list of environments."""

        response = self.client.get(
            '/api/v3/environment/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_list_envs_rel_envvip(self):
        """Test of success of the list of environments related with
        environments vip.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_success_list_envs_by_envvip(self):
        """Test of success of the list of environments by environment vip id.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_error_one_environment(self):
        """Test of error for get one environment."""

        response = self.client.get(
            '/api/v3/environment/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            404,
            response.status_code,
            'Status code should be 404 and was %s' % response.status_code
        )

    def test_get_error_list_envs_by_envvip(self):
        """Test of error of the list of environments by nonexistent id of the
        vip environment.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            404,
            response.status_code,
            'Status code should be 404 and was %s' % response.status_code
        )

    def test_post_one_env_success(self):
        name_file = 'api_environment/tests/json/post_one_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
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
            '/api/v3/environment/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Removes property id/name
        data = response.data
        del data['environments'][0]['id']
        del data['environments'][0]['name']
        # Tests if data was inserted
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_post_two_env_success(self):
        name_file = 'api_environment/tests/json/post_two_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(201, response.status_code,
                         'Status code should be 201 and was %s' %
                         response.status_code)

        id_env_one = response.data[0]['id']
        id_env_two = response.data[1]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/environment/%s;%s/' % (id_env_one, id_env_two),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Removes property id/name in each dict
        data = response.data
        del data['environments'][0]['id']
        del data['environments'][0]['name']
        del data['environments'][1]['id']
        del data['environments'][1]['name']

        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_put_one_env_success(self):
        name_file = 'api_environment/tests/json/put_one_env.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/6/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/6/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Removes property name
        data = response.data
        del data['environments'][0]['name']

        # Tests if data was updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_put_two_env_success(self):
        name_file = 'api_environment/tests/json/put_two_env.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/7;8/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/7;8/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Removes property name in each dict
        data = response.data
        del data['environments'][0]['name']
        del data['environments'][1]['name']

        # Tests if data was updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_put_one_env_duplicate_error(self):
        name_file = 'api_environment/tests/json/put_one_env_duplicate_error.json'

        # Does put request
        response = self.client.put(
            '/api/v3/environment/6/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(400, response.status_code,
                         'Status code should be 400 and was %s' %
                         response.status_code)

    def test_post_one_env_duplicate_error(self):
        name_file = 'api_environment/tests/json/post_one_env_duplicate_error.json'

        # Does post request
        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(400, response.status_code,
                         'Status code should be 400 and was %s' %
                         response.status_code)

    def test_delete_one_env_success(self):
        # Does post request
        response = self.client.delete(
            '/api/v3/environment/9/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/9/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(404, response.status_code,
                         'Status code should be 404 and was %s' %
                         response.status_code)

    def test_delete_two_env_success(self):
        # Does post request
        response = self.client.delete(
            '/api/v3/environment/10;11/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/10;11/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(404, response.status_code,
                         'Status code should be 404 and was %s' %
                         response.status_code)

    def test_delete_one_env_inexistent_error(self):
        # Does post request
        response = self.client.delete(
            '/api/v3/environment/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(404, response.status_code,
                         'Status code should be 404 and was %s' %
                         response.status_code)

    def test_delete_two_env_inexistent_error(self):
        # Does post request
        response = self.client.delete(
            '/api/v3/environment/1000;1001/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(404, response.status_code,
                         'Status code should be 404 and was %s' %
                         response.status_code)

    def test_delete_env_with_vlan_success(self):

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/6/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Vlan - Status code should be 200 and was %s' %
                         response.status_code)

        # Does post request
        response = self.client.delete(
            '/api/v3/environment/12/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Environment - Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/environment/12/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(404, response.status_code,
                         'Environment - Status code should be 404 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/6/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(404, response.status_code,
                         'Vlan - Status code should be 404 and was %s' %
                         response.status_code)
