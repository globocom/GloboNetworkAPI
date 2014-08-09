# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.ip.models import Ip, Ipv6
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, string_generator
import httplib


class IpConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/vlan/fixtures/initial_data.yaml']
    XML_KEY = "ips"

    # Environment
    ID_ENVIRONMENT_VALID = 20

    # Vlan
    ID_VLAN_VALID = 20

    # Network Ipv4
    ID_NETIPV4_VALID = 20

    # Network Ipv6
    ID_NETIPV6_VALID = 20

    # IPV4
    OBJ_IPV4 = Ip

    ID_IPV4_VALID = 1
    ID_IPV4_ALTER_VALID = 2
    ID_IPV4_REMOVE_VALID = 3

    # IPV6
    OBJ_IPV6 = Ipv6

    ID_IPV6_VALID = 1
    ID_IPV6_ALTER_VALID = 2
    ID_IPV6_REMOVE_VALID = 3

    # Valid equipment

    ID_EQUIP_VALID = 25

    # URLS
    URL_GET_BY_ID_IPV4 = '/ip/get-ipv4/%s/'
    URL_GET_BY_ID_IPV6 = '/ip/get-ipv6/%s/'
    URL_GET_BY_IP_ENV = '/ip/%s/ambiente/%s/'
    URL_GET_BY_IPV6_ENV = '/ipv6/environment/'
    URL_GET_BY_ID2_IPV4 = '/ip/get/%s/'
    URL_GET_BY_ID2_IPV6 = '/ipv6/get/%s/'
    URL_GET_IP4_OR_IP6 = '/ip/getbyoctblock/'
    URL_GET_AVAILABLE_IP4 = '/ip/availableip4/%s/'
    URL_GET_AVAILABLE_IP6 = '/ip/availableip6/%s/'
    URL_FIND_BY_NET_IP4 = '/ip/id_network_ipv4/%s/'
    URL_FIND_BY_NET_IP6 = '/ip/id_network_ipv6/%s/'
    URL_FIND_BY_EQUIP = '/ip/getbyequip/%s/'
    URL_ASSOC_IPV4 = '/ipv4/assoc/'
    URL_ASSOC_IPV6 = '/ipv6/assoc/'
    URL_SAVE_IPV4 = '/ipv4/save/'
    URL_SAVE_IPV6 = '/ipv6/save/'
    URL_DELETE_IPV4 = '/ip4/delete/%s/'
    URL_DELETE_IPV6 = '/ipv6/delete/%s/'
    URL_ALTER_IPV4 = '/ip4/edit/'
    URL_ALTER_IPV6 = '/ipv6/edit/'
    URL_CHECK_VIP_IP = '/ip/checkvipip/'
    URL_GET_AVAILABLE_VIP_IPV4 = '/ip/availableip4/vip/%s/'
    URL_GET_AVAILABLE_VIP_IPV6 = '/ip/availableip6/vip/%s/'
    URL_GET_IP_BY_EQUIP_VIP = '/ip/getbyequipandevip/'

    # Ips to search
    IP_VALID_FOR_GET_IP_ENV = '192.168.20.11'
    IPV6_VALID_FOR_GET_IPV6_ENV = 'ffab:cdef:ffff:ffff:0000:0000:0000:0011'

    # Vip environment
    ID_VIP_ENVIRONMENT_VALID = 1

    # Ipv4 mock
    def mock_save_ipv4_valid(self):
        mock = {}
        mock['id_net'] = self.ID_NETIPV4_VALID
        mock['descricao'] = 'Ip valid description'
        mock['ip4'] = '192.168.20.101'
        mock['id_equip'] = self.ID_EQUIP_VALID
        return mock

    def mock_alter_ipv4_valid(self):
        mock = {}
        mock['id_ip'] = self.ID_IPV4_ALTER_VALID
        mock['descricao'] = 'Ipv4 new description'
        mock['ip4'] = '192.168.20.131'
        return mock

    # Ipv6 mock
    def mock_save_ipv6_valid(self):
        mock = {}
        mock['id_net'] = self.ID_NETIPV6_VALID
        mock['descricao'] = 'Ipv6 valid description'
        mock['ip6'] = 'ffab:cdef:ffff:ffff:0000:0000:0000:0101'
        mock['id_equip'] = self.ID_EQUIP_VALID
        return mock

    def mock_alter_ipv6_valid(self):
        mock = {}
        mock['id_ip'] = self.ID_IPV6_ALTER_VALID
        mock['descricao'] = 'Ipv6 new description'
        mock['ip6'] = 'ffab:cdef:ffff:ffff:0000:0000:0000:0201'
        return mock

    # Ipv6 search by ipv6 and environment mock
    def mock_for_ipv6_env_search(self):
        mock = {}
        mock['ipv6'] = self.IPV6_VALID_FOR_GET_IPV6_ENV
        mock['id_environment'] = self.ID_ENVIRONMENT_VALID
        return mock

    def mock_for_assoc(self):
        mock = {}
        mock['id_ip'] = 4
        mock['id_net'] = 20
        mock['id_equip'] = 26
        return mock

    def mock_for_check_vip(self):
        mock = {}
        mock['ip'] = '192.168.55.121'
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        return mock

    def mock_for_ip_equip_vip(self):
        mock = {}
        mock['equip_name'] = 'BALANCINGEQUIPFORVIP1'
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        return mock

    def search_ipv6_env(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_for_ipv6_env_search()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_GET_BY_IPV6_ENV, {'ipv6_map': mock})
        return response

    def get4or6(self, arg, client=CLIENT_TYPES.TEST):
        mock = {}
        mock['ip'] = arg
        response = self.switch(client).postXML(
            self.URL_GET_IP4_OR_IP6, {'ip_map': mock})
        return response

    def assoc_ipv4(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_for_assoc()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_ASSOC_IPV4, {'ip_map': mock})
        return response

    def assoc_ipv6(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_for_assoc()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_ASSOC_IPV6, {'ip_map': mock})
        return response

    def check_vip_ip(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_for_check_vip()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_CHECK_VIP_IP, {'ip_map': mock})
        return response

    def get_ip_by_equip_vip(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_for_ip_equip_vip()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_GET_IP_BY_EQUIP_VIP, {'ip_map': mock})
        return response

    def save_ipv4_attr_invalid(self, value, code=None):
        mock = self.mock_save_ipv4_valid()
        mock[self.KEY_ATTR] = value
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPV4, {'ip_map': mock})
        self._attr_invalid(response, code)

    def alter_ipv4_attr_invalid(self, value, code=None):
        mock = self.mock_alter_ipv4_valid()
        mock[self.KEY_ATTR] = value
        response = self.client_autenticado().postXML(
            self.URL_ALTER_IPV4, {'ip_map': mock})
        self._attr_invalid(response, code)

    def save_ipv6_attr_invalid(self, value, code=None):
        mock = self.mock_save_ipv6_valid()
        mock[self.KEY_ATTR] = value
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPV6, {'ip_map': mock})
        self._attr_invalid(response, code)

    def alter_ipv6_attr_invalid(self, value, code=None):
        mock = self.mock_alter_ipv6_valid()
        mock[self.KEY_ATTR] = value
        response = self.client_autenticado().postXML(
            self.URL_ALTER_IPV6, {'ip_map': mock})
        self._attr_invalid(response, code)

    def ip_from_octs(self, obj):
        return str(str(obj['oct1']) + '.' + str(obj['oct2']) + '.' + str(obj['oct3']) + '.' + str(obj['oct4']))

    def ip_from_blocks(self, obj):
        return str(str(obj['block1']) + ':' + str(obj['block2']) + ':' + str(obj['block3']) + ':' + str(obj['block4']) + ':' + str(obj['block5']) + ':' + str(obj['block6']) + ':' + str(obj['block7']) + ':' + str(obj['block8']))

    def valid_ipv4_attr(self, mock, obj):
        assert mock['descricao'] == obj['descricao']
        assert mock['ip4'] == self.ip_from_octs(obj)

    def valid_ipv6_attr(self, mock, obj):
        assert mock['descricao'] == obj['description']
        assert mock['ip6'] == self.ip_from_blocks(obj)


class Ipv4ConsultationTest(IpConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.IP_NOT_FOUND
    ID_VALID = IpConfigTest.ID_IPV4_VALID
    URL_GET_BY_ID = IpConfigTest.URL_GET_BY_ID_IPV4

    def test_get_by_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response)
        valid_content(response, 'ipv4')

    def test_get_by_id_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_get_by_id_negative(self):
        self.get_by_id_negative()

    def test_get_by_id_letter(self):
        self.get_by_id_letter()

    def test_get_by_id_zero(self):
        self.get_by_id_zero()

    def test_get_by_id_empty(self):
        self.get_by_id_empty()


class Ipv6ConsultationTest(IpConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.IP_NOT_FOUND
    ID_VALID = IpConfigTest.ID_IPV6_VALID
    URL_GET_BY_ID = IpConfigTest.URL_GET_BY_ID_IPV6

    def test_get_by_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response)
        valid_content(response, 'ipv6')

    def test_get_by_id_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_get_by_id_negative(self):
        self.get_by_id_negative()

    def test_get_by_id_letter(self):
        self.get_by_id_letter()

    def test_get_by_id_zero(self):
        self.get_by_id_zero()

    def test_get_by_id_empty(self):
        self.get_by_id_empty()


class IpGetByIpEnvConsultationTest(IpConfigTest, AttrTest):

    def test_get_by_ip_env_valid(self):
        response = self.client_autenticado().get(self.URL_GET_BY_IP_ENV %
                                                 (self.IP_VALID_FOR_GET_IP_ENV, self.ID_ENVIRONMENT_VALID))
        valid_response(response)
        valid_content(response, 'ip')

    def test_get_by_ip_env_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_BY_IP_ENV %
                                                   (self.IP_VALID_FOR_GET_IP_ENV, self.ID_ENVIRONMENT_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ip_env_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_BY_IP_ENV %
                                                        (self.IP_VALID_FOR_GET_IP_ENV, self.ID_ENVIRONMENT_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ip_env_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % (self.IP_VALID_FOR_GET_IP_ENV, self.ID_NONEXISTENT))
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_get_by_ip_env_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % (self.IP_VALID_FOR_GET_IP_ENV, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_get_by_ip_env_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % (self.IP_VALID_FOR_GET_IP_ENV, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_get_by_ip_env_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % (self.IP_VALID_FOR_GET_IP_ENV, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_get_by_ip_env_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % (self.IP_VALID_FOR_GET_IP_ENV, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_get_by_ip_nonexistent_env(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % ('192.168.30.1', self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_get_by_ip_invalid_chars_env(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % ('192.168.20.1za', self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)

    def test_get_by_ip_invalid_range_env(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % ('192.168.20.1000', self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)

    def test_get_by_ip_invalid_comma_env(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % ('192,168,20,11', self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)

    def test_get_by_ip_invalid_separators_env(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IP_ENV % ('192.168/20;11', self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)


class IpFindByIdConsultationTest(IpConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.IP_NOT_FOUND
    ID_VALID = IpConfigTest.ID_IPV4_VALID
    URL_GET_BY_ID = IpConfigTest.URL_GET_BY_ID2_IPV4

    def test_find_by_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_find_by_id_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_find_by_id_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_find_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_find_by_id_negative(self):
        self.get_by_id_negative()

    def test_find_by_id_letter(self):
        self.get_by_id_letter()

    def test_find_by_id_zero(self):
        self.get_by_id_zero()

    def test_find_by_id_empty(self):
        self.get_by_id_empty()


class Ipv6FindByIdConsultationTest(IpConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.IP_NOT_FOUND
    ID_VALID = IpConfigTest.ID_IPV6_VALID
    URL_GET_BY_ID = IpConfigTest.URL_GET_BY_ID2_IPV6

    def test_find_by_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_find_by_id_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_find_by_id_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_find_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_find_by_id_negative(self):
        self.get_by_id_negative()

    def test_find_by_id_letter(self):
        self.get_by_id_letter()

    def test_find_by_id_zero(self):
        self.get_by_id_zero()

    def test_find_by_id_empty(self):
        self.get_by_id_empty()


class Ipv6GetByIpEnvConsultationTest(IpConfigTest, AttrTest):

    def test_get_by_ipv6_env_valid(self):
        response = self.search_ipv6_env()
        valid_response(response)
        valid_content(response, 'ipv6')

    def test_get_by_ipv6_env_no_permission(self):
        response = self.search_ipv6_env(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ipv6_env_no_read_permission(self):
        response = self.search_ipv6_env(client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ipv6_env_nonexistent(self):
        response = self.search_ipv6_env(
            {'id_environment': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_get_by_ipv6_env_negative(self):
        response = self.search_ipv6_env({'id_environment': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv6_env_letter(self):
        response = self.search_ipv6_env({'id_environment': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv6_env_zero(self):
        response = self.search_ipv6_env({'id_environment': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv6_env_empty(self):
        response = self.search_ipv6_env({'id_environment': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv6_nonexistent_env(self):
        response = self.search_ipv6_env(
            {'ipv6': 'ffab:cdef:ffff:ffff:0000:0000:0000:0015'})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_get_by_ipv6_invalid_chars_env(self):
        response = self.search_ipv6_env(
            {'ipv6': 'ffab:cdef:ffff:ffff:0000:0000:0000:0t1g'})
        self._attr_invalid(response)

    def test_get_by_ipv6_invalid_range_env(self):
        response = self.search_ipv6_env(
            {'ipv6': 'ffab:cdef:ffff:ffff:0000:0000:0000:150000'})
        self._attr_invalid(response)

    def test_get_by_ipv6_invalid_comma_env(self):
        response = self.search_ipv6_env(
            {'ipv6': 'ffab,cdef,ffff,ffff,0000,0000,0000,0011'})
        self._attr_invalid(response)

    def test_get_by_ipv6_invalid_separators_env(self):
        response = self.search_ipv6_env(
            {'ipv6': 'ffab:cdef;ffff:ffff/0000:0000:0000:0015'})
        self._attr_invalid(response)


class IpGet4or6ConsultationTest(IpConfigTest, AttrTest):

    def test_get_4or6_valid_4(self):
        response = self.get4or6('192.168.20.11')
        valid_response(response)
        valid_content(response)

    def test_get_4or6_valid_6(self):
        response = self.get4or6('ffab:cdef:ffff:ffff:0000:0000:0000:0011')
        valid_response(response)
        valid_content(response)

    def test_get_4or6_no_permission(self):
        response = self.get4or6(
            '192.168.20.11', client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_4or6_no_read_permission(self):
        response = self.get4or6(
            '192.168.20.11', client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_4or6_nonexistent_4(self):
        response = self.get4or6('192.168.30.1')
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_get_4or6_invalid_chars_4(self):
        response = self.get4or6('192.168.20.1za')
        self._attr_invalid(response)

    def test_get_4or6_invalid_range_4(self):
        response = self.get4or6('192.168.20.1000')
        self._attr_invalid(response)

    def test_get_4or6_invalid_comma_4(self):
        response = self.get4or6('192,168,20,11')
        self._attr_invalid(response)

    def test_get_4or6_invalid_separators_4(self):
        response = self.get4or6('192.168/20;11')
        self._attr_invalid(response)

    def test_get_4or6_nonexistent_6(self):
        response = self.get4or6('ffab:cdef:ffff:ffff:0000:0000:0000:0015')
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_get_4or6_invalid_chars_6(self):
        response = self.get4or6('ffab:cdef:ffff:ffff:0000:0000:0000:0t1g')
        self._attr_invalid(response)

    def test_get_4or6_invalid_range_6(self):
        response = self.get4or6('ffab:cdef:ffff:ffff:0000:0000:0000:150000')
        self._attr_invalid(response)

    def test_get_4or6_invalid_comma_6(self):
        response = self.get4or6('ffab,cdef,ffff,ffff,0000,0000,0000,0011')
        self._attr_invalid(response)

    def test_get_4or6_invalid_separators_6(self):
        response = self.get4or6('ffab:cdef;ffff:ffff/0000:0000:0000:0015')
        self._attr_invalid(response)


class IpGetAvailableIpv4ConsultationTest(IpConfigTest, AttrTest):

    def test_get_available_ip4_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP4 % self.ID_NETIPV4_VALID)
        valid_response(response)
        valid_content(response, 'ip')

    def test_get_available_ip4_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_AVAILABLE_IP4 % self.ID_NETIPV4_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_ip4_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_AVAILABLE_IP4 % self.ID_NETIPV4_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_ip4_net_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP4 % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV4_NOT_FOUND)

    def test_get_available_ip4_net_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP4 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip4_net_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP4 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip4_net_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP4 % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip4_net_none(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP4 % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip4_net_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP4 % self.LETTER_ATTR)
        self._attr_invalid(response)


class IpGetAvailableIpv6ConsultationTest(IpConfigTest, AttrTest):

    def test_get_available_ip6_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP6 % self.ID_NETIPV6_VALID)
        valid_response(response)
        valid_content(response, 'ip6')

    def test_get_available_ip6_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_AVAILABLE_IP6 % self.ID_NETIPV6_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_ip6_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_AVAILABLE_IP6 % self.ID_NETIPV6_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_ip6_net_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP6 % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV6_NOT_FOUND)

    def test_get_available_ip6_net_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP6 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip6_net_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP6 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip6_net_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP6 % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip6_net_none(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP6 % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_get_available_ip6_net_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_AVAILABLE_IP6 % self.LETTER_ATTR)
        self._attr_invalid(response)


class IpFindByNetIp4ConsultationTest(IpConfigTest, AttrTest):

    def test_get_by_net_ip4_valid(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP4 % self.ID_NETIPV4_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_net_ip4_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_FIND_BY_NET_IP4 % self.ID_NETIPV4_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_net_ip4_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_FIND_BY_NET_IP4 % self.ID_NETIPV4_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_net_ip4_net_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP4 % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV4_NOT_FOUND)

    def test_get_by_net_ip4_net_negative(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP4 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip4_net_zero(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP4 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip4_net_empty(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP4 % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip4_net_none(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP4 % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip4_net_letter(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP4 % self.LETTER_ATTR)
        self._attr_invalid(response)


class IpFindByNetIp6ConsultationTest(IpConfigTest, AttrTest):

    def test_get_by_net_ip6_valid(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP6 % self.ID_NETIPV6_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_net_ip6_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_FIND_BY_NET_IP6 % self.ID_NETIPV6_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_net_ip6_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_FIND_BY_NET_IP6 % self.ID_NETIPV6_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_net_ip6_net_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP6 % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV6_NOT_FOUND)

    def test_get_by_net_ip6_net_negative(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP6 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip6_net_zero(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP6 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip6_net_empty(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP6 % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip6_net_none(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP6 % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_get_by_net_ip6_net_letter(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_NET_IP6 % self.LETTER_ATTR)
        self._attr_invalid(response)


class IpFindByEquipConsultationTest(IpConfigTest, AttrTest):

    def test_find_by_equip_valid(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_EQUIP % self.ID_EQUIP_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_find_by_equip_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_FIND_BY_EQUIP % self.ID_EQUIP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_find_by_equip_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_FIND_BY_EQUIP % self.ID_EQUIP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_find_by_equip_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_EQUIP % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_find_by_equip_negative(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_EQUIP % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_find_by_equip_zero(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_EQUIP % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_find_by_equip_empty(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_EQUIP % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_find_by_equip_none(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_EQUIP % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_find_by_equip_letter(self):
        response = self.client_autenticado().get(
            self.URL_FIND_BY_EQUIP % self.LETTER_ATTR)
        self._attr_invalid(response)


class IpAssocIpv4Test(IpConfigTest, AttrTest):

    def test_assoc_ipv4_valid(self):
        response = self.assoc_ipv4()
        valid_response(response)

    def test_assoc_ipv4_no_permission(self):
        response = self.assoc_ipv4(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_assoc_ipv4_no_write_permission(self):
        response = self.assoc_ipv4(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_assoc_ipv4_ip_negative(self):
        response = self.assoc_ipv4(dicts={'id_ip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_ip_zero(self):
        response = self.assoc_ipv4(dicts={'id_ip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_ip_empty(self):
        response = self.assoc_ipv4(dicts={'id_ip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_ip_none(self):
        response = self.assoc_ipv4(dicts={'id_ip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_ip_letter(self):
        response = self.assoc_ipv4(dicts={'id_ip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_net_negative(self):
        response = self.assoc_ipv4(dicts={'id_net': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_net_zero(self):
        response = self.assoc_ipv4(dicts={'id_net': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_net_empty(self):
        response = self.assoc_ipv4(dicts={'id_net': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_net_none(self):
        response = self.assoc_ipv4(dicts={'id_net': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_net_letter(self):
        response = self.assoc_ipv4(dicts={'id_net': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_equip_negative(self):
        response = self.assoc_ipv4(dicts={'id_equip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_equip_zero(self):
        response = self.assoc_ipv4(dicts={'id_equip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_equip_empty(self):
        response = self.assoc_ipv4(dicts={'id_equip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_equip_none(self):
        response = self.assoc_ipv4(dicts={'id_equip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv4_equip_letter(self):
        response = self.assoc_ipv4(dicts={'id_equip': self.LETTER_ATTR})
        self._attr_invalid(response)


class IpAssocIpv6Test(IpConfigTest, AttrTest):

    def test_assoc_ipv6_valid(self):
        response = self.assoc_ipv6()
        valid_response(response)

    def test_assoc_ipv6_no_permission(self):
        response = self.assoc_ipv6(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_assoc_ipv6_no_write_permission(self):
        response = self.assoc_ipv6(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_assoc_ipv6_ip_negative(self):
        response = self.assoc_ipv6(dicts={'id_ip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_ip_zero(self):
        response = self.assoc_ipv6(dicts={'id_ip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_ip_empty(self):
        response = self.assoc_ipv6(dicts={'id_ip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_ip_none(self):
        response = self.assoc_ipv6(dicts={'id_ip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_ip_letter(self):
        response = self.assoc_ipv6(dicts={'id_ip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_net_negative(self):
        response = self.assoc_ipv6(dicts={'id_net': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_net_zero(self):
        response = self.assoc_ipv6(dicts={'id_net': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_net_empty(self):
        response = self.assoc_ipv6(dicts={'id_net': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_net_none(self):
        response = self.assoc_ipv6(dicts={'id_net': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_net_letter(self):
        response = self.assoc_ipv6(dicts={'id_net': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_equip_negative(self):
        response = self.assoc_ipv6(dicts={'id_equip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_equip_zero(self):
        response = self.assoc_ipv6(dicts={'id_equip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_equip_empty(self):
        response = self.assoc_ipv6(dicts={'id_equip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_equip_none(self):
        response = self.assoc_ipv6(dicts={'id_equip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_assoc_ipv6_equip_letter(self):
        response = self.assoc_ipv6(dicts={'id_equip': self.LETTER_ATTR})
        self._attr_invalid(response)


class Ipv4Test(IpConfigTest, AttrTest):

    URL_SAVE = IpConfigTest.URL_SAVE_IPV4

    def test_save_ipv4_valid(self):
        mock = self.mock_save_ipv4_valid()
        response = self.save({'ip_map': mock})
        valid_response(response)
        valid_content(response, 'ip')

    def test_save_ipv4_no_permission(self):
        mock = self.mock_save_ipv4_valid()
        response = self.save({'ip_map': mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv4_no_write_permission(self):
        mock = self.mock_save_ipv4_valid()
        response = self.save(
            {'ip_map': mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_alter_ipv4_valid()
        response = self.client_autenticado().postXML(
            self.URL_ALTER_IPV4, {'ip_map': mock})
        valid_response(response)
        ip = Ip.get_by_pk(self.ID_IPV4_ALTER_VALID)
        self.valid_ipv4_attr(mock, model_to_dict(ip))

    def test_alter_no_permission(self):
        mock = self.mock_alter_ipv4_valid()
        response = self.client_no_permission().postXML(
            self.URL_ALTER_IPV4, {'ip_map': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_alter_ipv4_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ALTER_IPV4, {'ip_map': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class Ipv6Test(IpConfigTest, AttrTest):

    URL_SAVE = IpConfigTest.URL_SAVE_IPV6

    def test_save_ipv6_valid(self):
        mock = self.mock_save_ipv6_valid()
        response = self.save({'ip_map': mock})
        valid_response(response)
        valid_content(response, 'ipv6')

    def test_save_ipv6_no_permission(self):
        mock = self.mock_save_ipv6_valid()
        response = self.save({'ip_map': mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv6_no_write_permission(self):
        mock = self.mock_save_ipv6_valid()
        response = self.save(
            {'ip_map': mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_alter_ipv6_valid()
        response = self.client_autenticado().postXML(
            self.URL_ALTER_IPV6, {'ip_map': mock})
        valid_response(response)
        ip = Ipv6.get_by_pk(self.ID_IPV6_ALTER_VALID)
        self.valid_ipv6_attr(mock, model_to_dict(ip))

    def test_alter_no_permission(self):
        mock = self.mock_alter_ipv6_valid()
        response = self.client_no_permission().postXML(
            self.URL_ALTER_IPV6, {'ip_map': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_alter_ipv6_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ALTER_IPV6, {'ip_map': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class Ipv4RemoveTest(IpConfigTest, RemoveTest):

    URL_REMOVE = IpConfigTest.URL_DELETE_IPV4
    CODE_ERROR_NOT_FOUND = CodeError.IP_NOT_FOUND

    def remove(self, idt):
        response = self.client_autenticado().get(self.URL_REMOVE % idt)
        return response

    def test_remove_valid(self):
        response = self.remove(self.ID_IPV4_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_REMOVE % self.ID_IPV4_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().get(
            self.URL_REMOVE % self.ID_IPV4_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_negative(self):
        self.remove_negative()

    def test_remove_letter(self):
        self.remove_letter()

    def test_remove_zero(self):
        self.remove_zero()

    def test_remove_empty(self):
        self.remove_empty()


class Ipv6RemoveTest(IpConfigTest, RemoveTest):

    URL_REMOVE = IpConfigTest.URL_DELETE_IPV6
    CODE_ERROR_NOT_FOUND = CodeError.IP_NOT_FOUND

    def remove(self, idt):
        response = self.client_autenticado().get(self.URL_REMOVE % idt)
        return response

    def test_remove_valid(self):
        response = self.remove(self.ID_IPV6_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_REMOVE % self.ID_IPV6_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().get(
            self.URL_REMOVE % self.ID_IPV6_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_negative(self):
        self.remove_negative()

    def test_remove_letter(self):
        self.remove_letter()

    def test_remove_zero(self):
        self.remove_zero()

    def test_remove_empty(self):
        self.remove_empty()


class Ipv4NetworkAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'id_net'

    def test_save_nonexistent(self):
        self.save_ipv4_attr_invalid(
            self.ID_NONEXISTENT, CodeError.NETWORK_IPV4_NOT_FOUND)

    def test_save_negative(self):
        self.save_ipv4_attr_invalid(self.NEGATIVE_ATTR)

    def test_save_letter(self):
        self.save_ipv4_attr_invalid(self.LETTER_ATTR)

    def test_save_zero(self):
        self.save_ipv4_attr_invalid(self.ZERO_ATTR)

    def test_save_empty(self):
        self.save_ipv4_attr_invalid(self.EMPTY_ATTR)

    def test_save_none(self):
        self.save_ipv4_attr_invalid(self.NONE_ATTR)


class Ipv4DescriptionAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'descricao'

    def test_save_minsize(self):
        self.save_ipv4_attr_invalid(string_generator(2))

    def test_save_maxsize(self):
        self.save_ipv4_attr_invalid(string_generator(101))

    def test_alter_minsize(self):
        self.alter_ipv4_attr_invalid(string_generator(2))

    def test_alter_maxsize(self):
        self.alter_ipv4_attr_invalid(string_generator(101))


class Ipv4IpAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'ip4'

    def test_save_invalid(self):
        self.save_ipv4_attr_invalid(string_generator(5))

    def test_save_comma(self):
        self.save_ipv4_attr_invalid('192,168,20,101')

    def test_save_separators(self):
        self.save_ipv4_attr_invalid('192.168/20;101')

    def test_save_range(self):
        self.save_ipv4_attr_invalid('192.168.20.1010')

    def test_alter_invalid(self):
        self.alter_ipv4_attr_invalid(string_generator(5))

    def test_alter_comma(self):
        self.alter_ipv4_attr_invalid('192,168,20,101')

    def test_alter_separators(self):
        self.alter_ipv4_attr_invalid('192.168/20;101')

    def test_alter_range(self):
        self.alter_ipv4_attr_invalid('192.168.20.1010')


class Ipv4EquipAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'id_equip'

    def test_save_nonexistent(self):
        self.save_ipv4_attr_invalid(
            self.ID_NONEXISTENT, CodeError.EQUIPMENT_NOT_FOUND)

    def test_save_negative(self):
        self.save_ipv4_attr_invalid(self.NEGATIVE_ATTR)

    def test_save_letter(self):
        self.save_ipv4_attr_invalid(self.LETTER_ATTR)

    def test_save_zero(self):
        self.save_ipv4_attr_invalid(self.ZERO_ATTR)

    def test_save_empty(self):
        self.save_ipv4_attr_invalid(self.EMPTY_ATTR)

    def test_save_none(self):
        self.save_ipv4_attr_invalid(self.NONE_ATTR)


class Ipv6NetworkAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'id_net'

    def test_save_nonexistent(self):
        self.save_ipv6_attr_invalid(
            self.ID_NONEXISTENT, CodeError.NETWORK_IPV6_NOT_FOUND)

    def test_save_negative(self):
        self.save_ipv6_attr_invalid(self.NEGATIVE_ATTR)

    def test_save_letter(self):
        self.save_ipv6_attr_invalid(self.LETTER_ATTR)

    def test_save_zero(self):
        self.save_ipv6_attr_invalid(self.ZERO_ATTR)

    def test_save_empty(self):
        self.save_ipv6_attr_invalid(self.EMPTY_ATTR)

    def test_save_none(self):
        self.save_ipv6_attr_invalid(self.NONE_ATTR)


class Ipv6DescriptionAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'descricao'

    def test_save_minsize(self):
        self.save_ipv6_attr_invalid(string_generator(2))

    def test_save_maxsize(self):
        self.save_ipv6_attr_invalid(string_generator(101))

    def test_alter_minsize(self):
        self.alter_ipv6_attr_invalid(string_generator(2))

    def test_alter_maxsize(self):
        self.alter_ipv6_attr_invalid(string_generator(101))


class Ipv6IpAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'ip6'

    def test_save_invalid(self):
        self.save_ipv6_attr_invalid(string_generator(20))

    def test_save_comma(self):
        self.save_ipv6_attr_invalid('ffab,cdef,ffff,ffff,0000,0000,0000,0101')

    def test_save_separators(self):
        self.save_ipv6_attr_invalid('ffab;cdef.ffff.ffff:0000/0000;0000:0101')

    def test_save_range(self):
        self.save_ipv6_attr_invalid('ffab:cdef:ffff:ffff:0000:0000:0000:90101')

    def test_alter_invalid(self):
        self.alter_ipv6_attr_invalid(string_generator(20))

    def test_alter_comma(self):
        self.alter_ipv6_attr_invalid('ffab,cdef,ffff,ffff,0000,0000,0000,0101')

    def test_alter_separators(self):
        self.alter_ipv6_attr_invalid('ffab;cdef.ffff.ffff:0000/0000;0000:0101')

    def test_alter_range(self):
        self.alter_ipv6_attr_invalid(
            'ffab:cdef:ffff:ffff:0000:0000:0000:90101')


class Ipv6EquipAttrTest(IpConfigTest, AttrTest):

    KEY_ATTR = 'id_equip'

    def test_save_nonexistent(self):
        self.save_ipv6_attr_invalid(
            self.ID_NONEXISTENT, CodeError.EQUIPMENT_NOT_FOUND)

    def test_save_negative(self):
        self.save_ipv6_attr_invalid(self.NEGATIVE_ATTR)

    def test_save_letter(self):
        self.save_ipv6_attr_invalid(self.LETTER_ATTR)

    def test_save_zero(self):
        self.save_ipv6_attr_invalid(self.ZERO_ATTR)

    def test_save_empty(self):
        self.save_ipv6_attr_invalid(self.EMPTY_ATTR)

    def test_save_none(self):
        self.save_ipv6_attr_invalid(self.NONE_ATTR)


class IpCheckVipIpTest(IpConfigTest, AttrTest):

    def test_check_vip_valid(self):
        response = self.check_vip_ip()
        valid_response(response)
        valid_content(response, 'ip')

    def test_check_vip_valid_ipv6(self):
        response = self.check_vip_ip(
            dicts={'ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:0121'})
        valid_response(response)
        valid_content(response, 'ip')

    def test_check_vip_no_permission(self):
        response = self.check_vip_ip(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_check_vip_no_read_permission(self):
        response = self.check_vip_ip(client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_check_vip_env_vip_nonexistent(self):
        response = self.check_vip_ip({'id_evip': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_check_vip_env_vip_letter(self):
        response = self.check_vip_ip({'id_evip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_check_vip_env_vip_zero(self):
        response = self.check_vip_ip({'id_evip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_check_vip_env_vip_negative(self):
        response = self.check_vip_ip({'id_evip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_check_vip_env_vip_empty(self):
        response = self.check_vip_ip({'id_evip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_check_vip_env_vip_none(self):
        response = self.check_vip_ip({'id_evip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_check_vip_invalid_ip(self):
        response = self.check_vip_ip({'ip': string_generator(5)})
        self._attr_invalid(response)

    def test_check_vip_comma_ip(self):
        response = self.check_vip_ip({'ip': '192,168,55,121'})
        self._attr_invalid(response)

    def test_check_vip_separators_ip(self):
        response = self.check_vip_ip({'ip': '192.168/55;121'})
        self._attr_invalid(response)

    def test_check_vip_range_ip(self):
        response = self.check_vip_ip({'ip': '192.168.55.1210'})
        self._attr_invalid(response)

    def test_check_vip_comma_ip6(self):
        response = self.check_vip_ip(
            {'ip': 'ffab,cdef,ffff,ffff,0000,0000,0000,0121'})
        self._attr_invalid(response)

    def test_check_vip_separators_ip6(self):
        response = self.check_vip_ip(
            {'ip': 'ffab;cdef.ffff.ffff:0000/0000;0000:0121'})
        self._attr_invalid(response)

    def test_check_vip_range_ip6(self):
        response = self.check_vip_ip(
            {'ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:90121'})
        self._attr_invalid(response)


class IpGetAvailableIpv4forVip(IpConfigTest, AttrTest):

    def test_get_available_for_vip_valid(self):
        mock = {}
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(self.URL_GET_AVAILABLE_VIP_IPV4 %
                                                     self.ID_VIP_ENVIRONMENT_VALID, {'ip_map': mock})
        valid_response(response)
        valid_content(response, 'ip')

    def test_get_available_for_vip_no_permission(self):

        mock = {}
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        mock['name'] = string_generator()

        response = self.client_no_permission().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.ID_VIP_ENVIRONMENT_VALID, {'ip_map': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_for_vip_no_write_permission(self):

        mock = {}
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        mock['name'] = string_generator()

        response = self.client_no_write_permission().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.ID_VIP_ENVIRONMENT_VALID, {'ip_map': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_for_vip_env_vip_nonexistent(self):

        mock = {}
        mock['id_evip'] = self.ID_NONEXISTENT
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.ID_NONEXISTENT, {'ip_map': mock})
        self._attr_invalid(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_get_available_for_vip_env_vip_letter(self):

        mock = {}
        mock['id_evip'] = self.LETTER_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.LETTER_ATTR, {'ip_map': mock})

        self._attr_invalid(response)

    def test_get_available_for_vip_env_vip_zero(self):

        mock = {}
        mock['id_evip'] = self.ZERO_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.ZERO_ATTR, {'ip_map': mock})
        self._attr_invalid(response)

    def test_get_available_for_vip_env_vip_negative(self):

        mock = {}
        mock['id_evip'] = self.NEGATIVE_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.NEGATIVE_ATTR, {'ip_map': mock})
        self._attr_invalid(response)

    def test_get_available_for_vip_env_vip_empty(self):

        mock = {}
        mock['id_evip'] = self.EMPTY_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.EMPTY_ATTR, {'ip_map': mock})
        self._attr_invalid(response)

    def test_get_available_for_vip_env_vip_none(self):

        mock = {}
        mock['id_evip'] = self.NONE_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV4 % self.NONE_ATTR, {'ip_map': mock})
        self._attr_invalid(response)


class IpGetAvailableIpv6forVip(IpConfigTest, AttrTest):

    def test_get_available_for_vip_valid(self):

        mock = {}
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(self.URL_GET_AVAILABLE_VIP_IPV6 %
                                                     self.ID_VIP_ENVIRONMENT_VALID, {'ip_map': mock})

        valid_response(response)
        valid_content(response, 'ip')

    def test_get_available_for_vip_no_permission(self):

        mock = {}
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        mock['name'] = string_generator()

        response = self.client_no_permission().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.ID_VIP_ENVIRONMENT_VALID, {'ip_map': mock})

        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_for_vip_no_write_permission(self):

        mock = {}
        mock['id_evip'] = self.ID_VIP_ENVIRONMENT_VALID
        mock['name'] = string_generator()

        response = self.client_no_write_permission().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.ID_VIP_ENVIRONMENT_VALID, {'ip_map': mock})

        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_available_for_vip_env_vip_nonexistent(self):

        mock = {}
        mock['id_evip'] = self.ID_NONEXISTENT
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.ID_NONEXISTENT, {'ip_map': mock})

        self._attr_invalid(response, CodeError.ENV_VIP_NOT_FOUND)

    @me
    def test_get_available_for_vip_env_vip_letter(self):

        mock = {}
        mock['id_evip'] = self.LETTER_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.LETTER_ATTR, {'ip_map': mock})

        self._attr_invalid(response)

    def test_get_available_for_vip_env_vip_zero(self):

        mock = {}
        mock['id_evip'] = self.ZERO_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.ZERO_ATTR, {'ip_map': mock})

        self._attr_invalid(response)

    def test_get_available_for_vip_env_vip_negative(self):

        mock = {}
        mock['id_evip'] = self.NEGATIVE_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.NEGATIVE_ATTR, {'ip_map': mock})

        self._attr_invalid(response)

    @me
    def test_get_available_for_vip_env_vip_empty(self):

        mock = {}
        mock['id_evip'] = self.EMPTY_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.EMPTY_ATTR, {'ip_map': mock})
        self._attr_invalid(response)

    def test_get_available_for_vip_env_vip_none(self):

        mock = {}
        mock['id_evip'] = self.NONE_ATTR
        mock['name'] = string_generator()

        response = self.client_autenticado().postXML(
            self.URL_GET_AVAILABLE_VIP_IPV6 % self.NONE_ATTR, {'ip_map': mock})

        self._attr_invalid(response)


class IpGetByEquipVipTest(IpConfigTest, AttrTest):

    def test_get_ip_by_equip_env_vip_valid(self):
        response = self.get_ip_by_equip_vip()
        valid_response(response)
        valid_content(response, 'ipv4')
        valid_content(response, 'ipv6')

    def test_get_ip_by_equip_env_vip_no_permission(self):
        response = self.get_ip_by_equip_vip(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_ip_by_equip_env_vip_no_read_permission(self):
        response = self.get_ip_by_equip_vip(
            client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_ip_env_vip_nonexistent(self):
        response = self.get_ip_by_equip_vip({'id_evip': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_get_ip_env_vip_letter(self):
        response = self.get_ip_by_equip_vip({'id_evip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_get_ip_env_vip_zero(self):
        response = self.get_ip_by_equip_vip({'id_evip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_get_ip_env_vip_negative(self):
        response = self.get_ip_by_equip_vip({'id_evip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_get_ip_env_vip_empty(self):
        response = self.get_ip_by_equip_vip({'id_evip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_get_ip_env_vip_none(self):
        response = self.get_ip_by_equip_vip({'id_evip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_get_ip_equip_name_nonexistent(self):
        response = self.get_ip_by_equip_vip({'equip_name': 'EQUIPNONEXISTENT'})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_get_ip_equip_name_minsize(self):
        response = self.get_ip_by_equip_vip(
            {'equip_name': string_generator(2)})
        self._attr_invalid(response)

    def test_get_ip_equip_name_maxsize(self):
        response = self.get_ip_by_equip_vip(
            {'equip_name': string_generator(81)})
        self._attr_invalid(response)

    def test_get_ip_equip_name_invalid(self):
        response = self.get_ip_by_equip_vip({'equip_name': 'teste'})
        self._attr_invalid(response)

    def test_get_ip_equip_name_empty(self):
        response = self.get_ip_by_equip_vip({'equip_name': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_get_ip_equip_name_none(self):
        response = self.get_ip_by_equip_vip({'equip_name': self.NONE_ATTR})
        self._attr_invalid(response)
