# -*- coding: utf-8 -*-
import json
import logging
import os
import urllib

from django.test.client import Client

from networkapi.api_ip import facade
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.ip.models import IpNotFoundError
from networkapi.test import load_json
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario


log = logging.getLogger(__name__)


class IPv4FunctionalTestV3(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')
        self.url_prefix_ids = '/api/v3/ipv4/%s/'
        self.url_prefix_gen = '/api/v3/ipv4/'
        self.status_code_msg = 'Status code should between (%s,%s) and was %s'
        self.array_len_msg_err = 'Array should contains %s elements'
        self.key_ips_be_present_err = 'Key "ips" should be present on response data'
        self.key_ips_not_be_present_err = 'Key "ips" should be present on response data'
        self.first_error_code = 400
        self.last_error_code = 599

    def tearDown(self):
        pass

    def test_try_get_existent_ipv4_by_id(self):

        id = 60

        url = self.url_prefix_ids % id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn('ips', response.data,
                      self.key_ips_be_present_err)

        ipv4 = response.data['ips'][0]

        self.assertEqual(id, ipv4['id'],
                         'IPv4 id retrieved should be equals')

    def test_try_get_non_existent_ipv4_by_id(self):

        id = 1000

        url = self.url_prefix_ids % id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn('ips', response.data,
                         self.key_ips_not_be_present_err)

    def test_try_get_two_existent_ipv4_by_id(self):

        ids = [60, 61]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn('ips', response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data['ips']

        expt_count = 2
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

        for ipv4 in ipsv4:
            self.assertIn(ipv4['id'], ids,
                          'IPv4 id retrieved should be equals')

    def test_try_get_two_non_existent_ipv4_by_id(self):

        ids = [1000, 1001]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn('ips', response.data,
                         self.key_ips_not_be_present_err)

    def test_try_get_one_existent_and_non_existent_ipv4_by_id(self):

        ids = [60, 1001]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn('ips', response.data,
                         self.key_ips_not_be_present_err)

    def test_try_get_one_existent_ipv4_by_search(self):

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 60
            }]
        }

        fields = ['ip_formated']

        url = self.prepare_url(self.url_prefix_gen,
                               search=search, fields=fields)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn('ips', response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data['ips']

        expt_count = 1
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

        self.assertIn({'ip_formated': '10.0.0.60'}, ipsv4)

    def test_try_get_two_existent_ipv4_by_search(self):

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 60
            }, {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 61
            }]
        }

        fields = ['ip_formated']

        url = self.prepare_url(self.url_prefix_gen,
                               search=search, fields=fields)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn('ips', response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data['ips']

        expt_count = 2
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

        self.assertIn({'ip_formated': '10.0.0.60'}, ipsv4)
        self.assertIn({'ip_formated': '10.0.0.61'}, ipsv4)

    def test_try_get_non_existent_ipv4_by_search(self):

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 200
            }]
        }

        url = self.prepare_url(self.url_prefix_gen, search=search)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn('ips', response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data['ips']

        expt_count = 0
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

    # DELETE functional tests

    def test_try_delete_existent_ipv4(self):

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/ipv4_10_0_0_62_net_5.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        id = response.data[0]['id']

        url = self.url_prefix_ids % id

        self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn('ips', response.data,
                         self.key_ips_be_present_err)

    def test_try_delete_non_existent_ipv4(self):
        id = 1000

        url = self.url_prefix_ids % id

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, response.status_code))

    def test_try_delete_two_existent_ipv4(self):

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/ipv4_10_0_0_[62,63]_net_5.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        ids = [id['id'] for id in response.data]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, response.status_code))

        self.assertNotIn('ips', response.data,
                         self.key_ips_be_present_err)

    def test_try_delete_two_non_existent_ipv4(self):

        ids = [1000, 1001]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, response.status_code))

    def test_try_delete_one_existent_and_non_existent_ipv4(self):
        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/ipv4_10_0_0_62_net_5.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        created_id = response.data[0]['id']

        ids = [created_id, 1000]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, response.status_code))

        url = self.url_prefix_ids % created_id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn('ips', response.data,
                         self.key_ips_not_be_present_err)

    # post tests

    def test_try_create_ip_in_full_network(self):

        pass

    def test_try_create_out_of_range_ip_in_network(self):

        pass

    def prepare_url(self, uri, **kwargs):
        """Convert dict for URL params
        """
        params = dict()
        for key in kwargs:
            if key in ('kind', 'include', 'exclude', 'fields'):
                params.update({
                    key: ','.join(kwargs.get(key))
                })
            elif key == 'search':
                params.update({
                    key: kwargs.get(key)
                })

        if params:
            params = urllib.urlencode(params)
            uri = '%s?%s' % (uri, params)

        return uri
