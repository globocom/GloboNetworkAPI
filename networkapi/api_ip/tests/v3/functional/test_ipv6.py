# -*- coding: utf-8 -*-
import json
import logging
import os

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from networkapi.util.geral import prepare_url


log = logging.getLogger(__name__)


class IPv6FunctionalTestV3(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')
        self.url_prefix_ids = '/api/v3/ipv6/%s/'
        self.url_prefix_gen = '/api/v3/ipv6/'
        self.status_code_msg = 'Status code should between (%s,%s) and was %s'
        self.array_len_msg_err = 'Array of %s should contains %s elements'
        self.key_ips_be_present_err = 'Key "ips" should be present on response data'
        self.key_ips_not_be_present_err = \
            'Key "ips" should be present on response data'
        self.first_error_code = 400
        self.last_error_code = 599
        self.first_success_code = 200
        self.last_success_code = 299
        self.ips_key = 'ips'
        self.equality_ips_at_network_err = \
            'It should not have two equal IP Addresses on same Network.'
        self.not_expect_ip_msg_err = \
            'IPv6 with id %s retrieved was not expect in response.'

    def tearDown(self):
        pass

    # GET functional tests

    def test_try_get_existent_ipv6_by_id(self):
        """Tests if NAPI can return an existing IPv6 by id."""

        id = 60

        url = self.url_prefix_ids % id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

        ipv6 = response.data[self.ips_key][0]

        self.assertEqual(id, ipv6['id'],
                         'IPv6 id retrieved should be equals')

    def test_try_get_non_existent_ipv6_by_id(self):
        """Tests if NAPI returns error when ask
        to return not existing IPv6 by id.
        """

        id = 1000

        url = self.url_prefix_ids % id

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertNotIn(self.ips_key, response.data,
                         self.key_ips_not_be_present_err)

    def test_try_get_two_existent_ipv6_by_id(self):
        """Tests if NAPI can return two existent IPv6's by ids."""

        ids = [60, 61]
        ids_str = ';'.join(str(id) for id in ids)

        url = self.url_prefix_ids % ids_str

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        self.assertIn(self.ips_key, response.data,
                      self.key_ips_be_present_err)

        ipsv6 = response.data[self.ips_key]

        expt_count = 2
        self.assertEqual(len(ipsv6), expt_count,
                         self.array_len_msg_err % ('Ips', expt_count))

        for ipv6 in ipsv6:
            self.assertIn(ipv6['id'], ids,
                          self.not_expect_ip_msg_err % ipv6['id'])

    def test_try_get_two_non_existent_ipv6_by_id(self):
        """Tests if NAPI returns a error when ask to
        return two non existing IPv6's by ids.
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

    def test_try_get_one_existent_and_non_existent_ipv6_by_id(self):
        """Tests if NAPI returns a error when ask to
        return a existing and not existing IPv6's by ids.
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

    def test_try_get_one_existent_ipv6_by_search(self):
        """Tests if NAPI returns a dict with one IPv6 Addresses
        given a search one existing IPv6 Addresses.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0060'
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

        ipsv6 = response.data[self.ips_key]

        expt_count = 1
        self.assertEqual(len(ipsv6), expt_count,
                         self.array_len_msg_err % ('Ips', expt_count))

        self.assertIn(
            {'ip_formated': 'fc00:0000:0000:0004:0000:0000:0000:0060'}, ipsv6)

    def test_try_get_two_existent_ipv6_by_search(self):
        """Tests if NAPI returns a dict with two IPv6 Addresses
        given a search making OR by two IPv6 Addresses.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0060'
            }, {
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0061'
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

        ipsv6 = response.data[self.ips_key]

        expt_count = 2
        self.assertEqual(len(ipsv6), expt_count,
                         self.array_len_msg_err % ('Ips', expt_count))

        self.assertIn(
            {'ip_formated': 'fc00:0000:0000:0004:0000:0000:0000:0060'}, ipsv6)
        self.assertIn(
            {'ip_formated': 'fc00:0000:0000:0004:0000:0000:0000:0061'}, ipsv6)

    def test_try_get_non_existent_ipv6_by_search(self):
        """Tests if NAPI returns a dict with zero IPv6 Addresses
        given a search by not existent IPv6 Address.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0200'
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

        ipsv6 = response.data[self.ips_key]

        expt_count = 0
        self.assertEqual(len(ipsv6), expt_count,
                         self.array_len_msg_err % ('Ips', expt_count))

    # DELETE functional tests

    def test_try_delete_existent_ipv6(self):
        """Tests if NAPI can delete a existent IPv6 Address."""

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

    def test_try_delete_non_existent_ipv6(self):
        """Tests if NAPI returns error on deleting
        a not existing IPv6 Addresses.
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

    def test_try_delete_two_non_existent_ipv6(self):
        """Tests if NAPI returns error on deleting
        two not existing IPv6 Addresses.
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

    def test_try_delete_one_existent_and_non_existent_ipv6(self):
        """Tests if NAPI deny delete at same time an existent
        and a not existent IPv6 Address.
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

    def test_try_delete_ipv6_assoc_to_equipment(self):
        """Tests if NAPI can delete an IPv6 Address associated
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

    def test_try_delete_two_existent_ipv6(self):
        """Tests of NAPI can delete at same time
        two existent IPv6 Addresses.
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
                         self.key_ips_not_be_present_err)

    def test_try_delete_ipv6_used_by_not_created_vip_request(self):
        """Tests if NAPI can delete an IPv6 Address used
        in a not deployed VIP Request.
        """

        id = 430

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

    def test_try_delete_ipv6_used_by_created_vip_request(self):
        """Tests if NAPI deny deleting of IPv6 Address used
        in deployed VIP Request.
        """

        id = 431

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
        """Tests if NAPI can allocate automatically an IPv6 Address
        in a Network with available addresses.
        """

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_auto_net_free.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        # Get all IP's of Network

        search = {
            'start_record': 0,
            'end_record': 255,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'networkipv6': 5
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

        # Verify if Network has at least two equal IPv6 Addresses
        # If not, auto IP allocation were successfully
        self.assertEqual(len(ips), len(set(ips)),
                         self.equality_ips_at_network_err)

    def test_try_create_invalid_ip(self):
        """Tests if NAPI deny manually creation of invalid IPv6 Address
        (e.g.: fc00:0000:0000:0004:0000:0000:0000:gggg).
        """

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_fc00_0000_0000_0004_0000_0000_0000_gggg_net_5.json')),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

    def test_try_create_ip_associating_to_equipment(self):
        """Tests if NAPI can allocate an IPv6 Address manually and associate it to
        an equipment in a Network with available addresses.
        """
        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_fc00_0000_0000_0004_0000_0000_0000_0099_net_5_eqpt_99'
                '.json')),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

    def test_try_create_ip_in_full_network(self):
        """Tests if NAPI deny an IPv6 manually creation in a full network."""

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_fc00_0000_0000_0004_0000_0000_0000_0005_net_8.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

    def test_try_create_out_of_range_ip_in_network(self):
        """Tests if NAPI deny out of range network IPv6 manually creation."""

        response = self.client.post(
            self.url_prefix_gen,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/out_of_range_ipv6_fc00_0000_0000_0005_0000_0000_0000_0005'
                '_net_5.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_error_code <= st_code <= self.last_error_code,
                        self.status_code_msg %
                        (self.first_error_code, self.last_error_code, st_code))

    # PUT functional tests

    def test_try_update_ip_associating_to_equipment(self):
        """Tests if NAPI can update IPv6 associating it to equipment."""

        id = 90

        url = self.url_prefix_ids % id
        response = self.client.put(
            url,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_put_90_net_5_eqpt_90.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        # API will return success but network will not be changed
        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        url = prepare_url(self.url_prefix_ids % id, fields=['equipments'])
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        eqpts_ipsv6 = response.data[self.ips_key][0]['equipments']

        # Verify if relationship between eqpt 90 and Ip 90 was persisted
        self.assertIn({'id': 90}, eqpts_ipsv6)

    def test_try_update_ip_disassociating_it_of_all_equipments(self):
        """Tests if NAPI can update IPv6 disassociating it of equipment and
        remove this IPv6 given it is not used in anymore equipment.
        """

        id = 91

        url = self.url_prefix_ids % id
        response = self.client.put(
            url,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_put_91_net_5_eqpt_none.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        url = prepare_url(self.url_prefix_ids % id, fields=['equipments'])

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

    def test_try_update_ip_disassociating_it_of_some_equipments(self):
        """Tests if NAPI can update IPv6 disassociating it of equipment and
           maintaning this IPv6 in database given it is used in anymore equipment.
        """

        id = 92

        url = self.url_prefix_ids % id
        response = self.client.put(
            url,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_put_92_net_5_eqpt_none.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        url = prepare_url(self.url_prefix_ids % id, fields=['equipments__id'])

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

        ipv6_eqpts = response.data[self.ips_key][0]['equipments']

        expt_count = 1
        self.assertEqual(len(ipv6_eqpts), expt_count,
                         self.array_len_msg_err % ('Equipments', expt_count))

        self.assertIn({'id': 93}, ipv6_eqpts,
                      'Equipment with id %s should be associated to this IPv6.')
        self.assertNotIn({'id': 94}, ipv6_eqpts,
                         'Equipment with id %s should not be associated to this IPv6.')

    def test_try_update_ip_disassociating_it_of_equipments_and_associating_to_others_after(self):
        """Tests if NAPI can update IPv6 disassociating it of equipment
        and at same time associating it to other equipment.
        """

        id = 93

        url = self.url_prefix_ids % id
        response = self.client.put(
            url,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_put_93_net_5_eqpt_none.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        url = prepare_url(self.url_prefix_ids % id, fields=['equipments__id'])

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

        ipv6_eqpts = response.data[self.ips_key][0]['equipments']

        expt_count = 3
        self.assertEqual(len(ipv6_eqpts), expt_count,
                         self.array_len_msg_err % ('Equipments', expt_count))

        self.assertIn({'id': 95}, ipv6_eqpts,
                      'Equipment with id %s should be associated to this IPv6.')
        self.assertIn({'id': 97}, ipv6_eqpts,
                      'Equipment with id %s should be associated to this IPv6.')
        self.assertIn({'id': 98}, ipv6_eqpts,
                      'Equipment with id %s should be associated to this IPv6.')
        self.assertNotIn({'id': 96}, ipv6_eqpts,
                         'Equipment with id %s should not be associated to this IPv6.')

    def test_try_update_ip_changing_network(self):
        """Tests if NAPI deny or ignore update of IPv6 Address changing its network."""
        id = 67

        url = self.url_prefix_ids % id
        response = self.client.put(
            url,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_put_67_net_8.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        # API will return success but network will not be changed
        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        url = prepare_url(self.url_prefix_ids % id, fields=['networkipv6'])

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        ipsv6 = response.data[self.ips_key]

        # Verify if Network has not changed
        self.assertIn({'networkipv6': 5}, ipsv6)

    def test_try_update_ip_changing_octets(self):
        """Tests if NAPI deny or ignore update of IPv6 Address changing its octets."""
        id = 67

        url = self.url_prefix_ids % id
        response = self.client.put(
            url,
            data=json.dumps(self.load_json_file(
                'api_ip/tests/v3/'
                'functional/json/ipv6_put_67_fc00_0000_0000_0004_0000_0000_0000_0068'
                '_net_5.json'
            )),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        st_code = response.status_code

        self.assertTrue(self.first_success_code <= st_code <= self.last_success_code,
                        self.status_code_msg %
                        (self.first_success_code, self.last_success_code, st_code))

        url = prepare_url(self.url_prefix_ids % id, fields=['ip_formated'])

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        ipsv6 = response.data[self.ips_key]

        # Verify if Octets has not changed
        self.assertIn(
            {'ip_formated': u'fc00:0000:0000:0004:0000:0000:0000:0067'}, ipsv6)
