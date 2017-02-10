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
from networkapi.util.geral import prepare_url


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
        self.first_success_code = 200
        self.last_success_code = 299
        self.ips_key = 'ips'
        self.equality_ips_at_network_err = 'It should not have two equal IP Addresses on same Network.'

    def tearDown(self):
        pass

    # GET functional tests

    def test_try_get_existent_ipv4_by_id(self):
        """Tests if NAPI can return an existing IP by id."""

        id = 60

        url = self.url_prefix_ids % id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

        ipv4 = response.data[self.ips_key][0]

        self.assertEqual(id, ipv4['id'],
                         'IPv4 id retrieved should be equals')

    def test_try_get_non_existent_ipv4_by_id(self):
        """Tests if NAPI returns error when ask
        to return not existing IP by id.
        """

        id = 1000

        url = self.url_prefix_ids % id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_not_be_present_err)

    def test_try_get_two_existent_ipv4_by_id(self):
        """Tests if NAPI can return two existent IP's by ids."""

        ids = [60, 61]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data[self.ips_key]

        expt_count = 2
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

        for ipv4 in ipsv4:
            self.assertIn(ipv4['id'], ids,
                          'IPv4 id retrieved should be equals')

    def test_try_get_two_non_existent_ipv4_by_id(self):
        """Tests if NAPI returns a error when ask to
        return two non existing IP's by ids.
        """

        ids = [1000, 1001]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_not_be_present_err)

    def test_try_get_one_existent_and_non_existent_ipv4_by_id(self):
        """Tests if NAPI returns a error when ask to
        return a existing and not existing IP's by ids.
        """

        ids = [60, 1001]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_not_be_present_err)

    def test_try_get_one_existent_ipv4_by_search(self):
        """Tests if NAPI returns a dict with one IP Addresses
        given a search one existing IP Addresses.
        """

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

        url = prepare_url(self.url_prefix_gen,
                          search=search, fields=fields)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data[self.ips_key]

        expt_count = 1
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

        self.assertIn({'ip_formated': '10.0.0.60'}, ipsv4)

    def test_try_get_two_existent_ipv4_by_search(self):
        """Tests if NAPI returns a dict with two IP Addresses
        given a search making OR by two IP Addresses.
        """

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

        url = prepare_url(self.url_prefix_gen,
                          search=search, fields=fields)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data[self.ips_key]

        expt_count = 2
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

        self.assertIn({'ip_formated': '10.0.0.60'}, ipsv4)
        self.assertIn({'ip_formated': '10.0.0.61'}, ipsv4)

    def test_try_get_non_existent_ipv4_by_search(self):
        """Tests if NAPI returns a dict with zero IP Addresses
        given a search by not existent IP Address.
        """

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

        url = prepare_url(self.url_prefix_gen, search=search)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

        ipsv4 = response.data[self.ips_key]

        expt_count = 0
        self.assertEqual(len(ipsv4), expt_count,
                         self.array_len_msg_err % expt_count)

    # DELETE functional tests

    def test_try_delete_existent_ipv4(self):
        """Tests if NAPI can delete a existent IP Address."""

        id = 66

        url = self.url_prefix_ids % id

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_be_present_err)

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

    def test_try_delete_non_existent_ipv4(self):
        """Tests if NAPI returns error on deleting
        a not existing IP Addresses.
        """

        id = 1000

        url = self.url_prefix_ids % id

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

    def test_try_delete_two_non_existent_ipv4(self):
        """Tests if NAPI returns error on deleting
        two not existing IP Addresses.
        """

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
                        (self.first_error_code, self.last_error_code, st_code))

    def test_try_delete_one_existent_and_non_existent_ipv4(self):
        """Tests if NAPI deny delete at same time an existent
        and a not existent IP Address.
        """

        existent_ip_id = 62

        ids = [existent_ip_id, 1000]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

        url = self.url_prefix_ids % existent_ip_id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

    def test_try_delete_ipv4_assoc_to_equipment(self):
        """Tests if NAPI can delete an IP Address associated
        to some equipment.
        """

        id = 63

        url = self.url_prefix_ids % id

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_not_be_present_err)

    def test_try_delete_two_existent_ipv4(self):
        """Tests of NAPI can delete at same time
        two existent IP Addresses.
        """

        ids = [64, 65]
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
                        (self.first_error_code, self.last_error_code, st_code))

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_be_present_err)

    def test_try_delete_ipv4_used_by_not_created_vip_request(self):
        """Tests if NAPI can delete an IP Address used
        in a not deployed VIP Request.
        """

        id = 130

        url = self.url_prefix_ids % id

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_not_be_present_err)

    def test_try_delete_ipv4_used_by_created_vip_request(self):
        """Tests if NAPI deny deleting of IP Address used
        in deployed VIP Request.
        """

        id = 131

        url = self.url_prefix_ids % id

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

    # POST functional tests

    def test_try_create_auto_ip(self):
        """Tests if NAPI can allocate automatically an IP Address
        in a Network with available addresses.
        """

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/ipv4_auto_net_free.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        # Get all IP's of Network

        fields = ['ip_formated']

        search = {
            'start_record': 0,
            'end_record': 255,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'networkipv4': 5
            }]
        }

        fields = ['ip_formated']

        url = prepare_url(self.url_prefix_gen,
                          search=search, fields=fields)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        ips = response.data[self.ips_key]

        ips = [ip['ip_formated'] for ip in ips]

        # Verify if Network has two equal IP Addresses
        # If not, auto IP allocation were successfully
        self.assertEqual(len(ips), len(set(ips)),
                         self.equality_ips_at_network_err)

    def test_try_create_invalid_ip(self):
        """Tests if NAPI deny manually creation of invalid IP Address
        (e.g.: 10.0.0.430).
        """

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/ipv4_10_0_0_430_net_5.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

    def test_try_create_ip_associating_to_equipment(self):
        """Tests if NAPI can allocate an IP Address manually and associate it to
        an equipment in a Network with available addresses.
        """
        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/ipv4_10_0_0_99_net_6_eqpt_99.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

    def test_try_create_ip_in_full_network(self):
        """Tests if NAPI deny an IP manually creation in a full network."""

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/ipv4_198_168_1_5_net_8.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

    def test_try_create_out_of_range_ip_in_network(self):
        """Tests if NAPI deny out of range network IP manually creation."""

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(load_json(
                '%s/networkapi/api_ip/tests/v3/functional/json/out_of_range_ipv4_172_0_0_5_net_5.json' % os.getcwd())),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))
