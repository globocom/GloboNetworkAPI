# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.ip.models import NetworkIPv4, NetworkIPv6
from networkapi.test import BasicTestCase, AttrTest, CodeError, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, string_generator
import httplib
from networkapi.infrastructure.ip_subnet_utils import MAX_IPV6_HOSTS,\
    MAX_IPV4_HOSTS


class NetworkConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/vlan/fixtures/initial_data.yaml']
    XML_KEY = "network"
    XML_KEY_ALTER = "net"
    XML_KEY_NETWORK_IP = "vlan"
    ATTR_KEY_IPS = 'ids'
    XML_KEY_IPS_NETWORK = "ips"

    # IPV4
    OBJ_NETWORK_IPV4 = NetworkIPv4
    ID_NETWORK_IPV4_VALID = 1
    ID_NETWORK_IPV4_REMOVE_VALID = 2
    ID_NETWORK_IPV4_ALTER_VALID = 3

    # IPV6
    OBJ_NETWORK_IPV6 = NetworkIPv6
    ID_NETWORK_IPV6_VALID = 1
    ID_NETWORK_IPV6_REMOVE_VALID = 2
    ID_NETWORK_IPV6_ALTER_VALID = 3

    TYPE_NETWORK_V4 = 'v4'
    TYPE_NETWORK_V6 = 'v6'
    ID_NETWORK_IPV4_INACTIVE = 15
    ID_NETWORK_IPV6_INACTIVE = 15

    # URLS
    URL_GET_BY_IPV4_ID = "/network/ipv4/id/%s/"
    URL_GET_BY_IPV6_ID = "/network/ipv6/id/%s/"
    URL_REMOVE_BY_IPV4_ID = "/network/ipv4/%s/deallocate/"
    URL_REMOVE_BY_IPV6_ID = "/network/ipv6/%s/deallocate/"
    URL_SAVE = "/network/add/"
    URL_ALTER = "/network/edit/"
    URL_SAVE_NETWORK_IPV4 = "/network/ipv4/add/"
    URL_SAVE_NETWORK_IPV6 = "/network/ipv6/add/"
    URL_REMOVE = "/network/remove/"

    URL_GET_IPS_BY_IPV4_ID = "/ip/id_network_ipv4/%s/"
    URL_GET_IPS_BY_IPV6_ID = "/ip/id_network_ipv6/%s/"

    # MOCK NETWORK
    def mock_network_valid(self):
        mock = {}
        mock['network'] = "192.168.1.0/24"
        mock['id_vlan'] = 15
        mock['id_network_type'] = 1
        mock['id_environment_vip'] = 3
        return mock

    def mock_networkIpv4_set_first_available_ip_valid(self):
        mock = {}
        mock['network'] = "192.168.172.0/24"
        mock['id_vlan'] = 51
        mock['id_network_type'] = 1
        mock['id_environment_vip'] = 4
        return mock

    def mock_networkIpv6_set_first_available_ip_valid(self):
        mock = {}
        mock['network'] = "2002:0000:0000:0000:0000:0000:caa8:a00/120"
        mock['id_vlan'] = 51
        mock['id_network_type'] = 1
        mock['id_environment_vip'] = 4
        return mock

    def mock_networkIpv4AddResource_set_first_available_ip_valid(self):
        mock = {}
        mock['id_vlan'] = 51
        mock['id_tipo_rede'] = 1
        mock['id_ambiente_vip'] = 4

        return mock

    def mock_networkIpv6AddResource_set_first_available_ip_valid(self):
        mock = {}
        mock['id_vlan'] = 52
        mock['id_tipo_rede'] = 1
        mock['id_ambiente_vip'] = 4

        return mock

    def mock_network_alter_valid(self):
        mock = {}
        mock['id_network'] = self.ID_NETWORK_IPV4_ALTER_VALID
        mock['ip_type'] = 0
        mock['id_net_type'] = 1
        mock['id_env_vip'] = 1
        return mock

    def valid_network_attr(self, mock, obj):
        assert mock["id_net_type"] == obj["network_type"]
        assert mock["id_env_vip"] == obj["ambient_vip"]

    def alter_network_attr_invalid(self, attr, key, code_error=None):
        mock = self.mock_network_alter_valid()
        mock[key] = attr
        response = self.client_autenticado().postXML(
            self.URL_ALTER, {self.XML_KEY_ALTER: mock})
        self._attr_invalid(response, code_error)

    # MOCK IPV4
    def mock_network_ip_valid(self):
        mock = {}
        mock['id_vlan'] = 16
        mock['id_tipo_rede'] = 1
        mock['id_ambiente_vip'] = 1
        return mock

    def mock_network_hosts_ip_valid(self):
        mock = {}
        mock['id_vlan'] = 16
        mock['id_tipo_rede'] = 1
        mock['id_ambiente_vip'] = 1
        mock['num_hosts'] = 240
        return mock

    def save_network_ip_attr_invalid(self, attr, key, url, code_error=None):
        mock = self.mock_network_ip_valid()
        mock[key] = attr
        response = self.client_autenticado().postXML(
            url, {self.XML_KEY_NETWORK_IP: mock})
        self._attr_invalid(response, code_error)

    def save_network_hosts_ip_attr_invalid(self, attr, key, url, code_error=None):
        mock = self.mock_network_ip_valid()
        mock[key] = attr
        response = self.client_autenticado().putXML(
            url, {self.XML_KEY_NETWORK_IP: mock})
        self._attr_invalid(response, code_error)

    def mock_network_v4(self):
        mock = dict()
        mock[self.XML_KEY] = {self.ATTR_KEY_IPS: str(
            self.ID_NETWORK_IPV4_VALID) + '-' + self.TYPE_NETWORK_V4}
        return mock

    def mock_network_v6(self):
        mock = dict()
        mock[self.XML_KEY] = {self.ATTR_KEY_IPS: str(
            self.ID_NETWORK_IPV6_VALID) + '-' + self.TYPE_NETWORK_V6}
        return mock


class NetworkIPV4ConsultationTest(NetworkConfigTest, AttrTest):

    def test_get_by_network_ipv4(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV4_ID % self.ID_NETWORK_IPV4_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY, True)

    def test_get_by_network_ipv4_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_IPV4_ID % self.ID_NETWORK_IPV4_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_network_ipv4_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_IPV4_ID % self.ID_NETWORK_IPV4_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_network_ipv4_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV4_ID % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV4_NOT_FOUND)

    def test_get_by_network_ipv4_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV4_ID % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_network_ipv4_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV4_ID % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_network_ipv4_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV4_ID % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_network_ipv4_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV4_ID % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_get_by_network_ipv6(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV6_ID % self.ID_NETWORK_IPV6_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY, True)

    def test_get_by_network_ipv6_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_IPV6_ID % self.ID_NETWORK_IPV6_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_network_ipv6_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_IPV6_ID % self.ID_NETWORK_IPV6_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_network_ipv6_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV6_ID % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV6_NOT_FOUND)

    def test_get_by_network_ipv6_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV6_ID % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_network_ipv6_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV6_ID % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_network_ipv6_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV6_ID % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_network_ipv6_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_IPV6_ID % self.EMPTY_ATTR)
        self._attr_invalid(response)


class NetworkRemoveTest(NetworkConfigTest, RemoveTest):

    def test_remove_network_ipv4_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.ID_NETWORK_IPV4_REMOVE_VALID)
        valid_response(response)

    def test_remove_network_ipv4_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.ID_NETWORK_IPV4_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_network_ipv4_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.ID_NETWORK_IPV4_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_network_ipv4_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV4_NOT_FOUND)

    def test_remove_network_ipv4_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv4_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv4_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv4_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv4_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV4_ID % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv6_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.ID_NETWORK_IPV6_REMOVE_VALID)
        valid_response(response)

    def test_remove_network_ipv6_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.ID_NETWORK_IPV6_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_network_ipv6_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.ID_NETWORK_IPV6_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_network_ipv6_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.NETWORK_IPV6_NOT_FOUND)

    def test_remove_network_ipv6_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv6_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv6_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv6_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_remove_network_ipv6_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_BY_IPV6_ID % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_remove_type_v4(self):
        response = self.client_autenticado().putXML(
            self.URL_REMOVE, self.mock_network_v4())
        valid_response(response)

    def test_remove_type_v6(self):
        response = self.client_autenticado().putXML(
            self.URL_REMOVE, self.mock_network_v6())
        valid_response(response)

    def test_remove_type_v4_inactive(self):
        mock = self.mock_network_v4()
        mock[self.XML_KEY][self.ATTR_KEY_IPS] = str(
            self.ID_NETWORK_IPV4_INACTIVE) + '-' + self.TYPE_NETWORK_V4
        response = self.client_autenticado().putXML(self.URL_REMOVE, mock)
        self._attr_invalid(response, CodeError.NETWORK_REMOVE_INACTIVE)

    def test_remove_type_v6_inactive(self):
        mock = self.mock_network_v6()
        mock[self.XML_KEY][self.ATTR_KEY_IPS] = str(
            self.ID_NETWORK_IPV6_INACTIVE) + '-' + self.TYPE_NETWORK_V6
        response = self.client_autenticado().putXML(self.URL_REMOVE, mock)
        self._attr_invalid(response, CodeError.NETWORK_REMOVE_INACTIVE)

    def test_remove_invalid_type_v4(self):
        mock = self.mock_network_v4()
        mock[self.XML_KEY][self.ATTR_KEY_IPS] = str(
            self.ID_NETWORK_IPV4_VALID) + '-' + self.LETTER_ATTR
        response = self.client_autenticado().putXML(self.URL_REMOVE, mock)
        self._attr_invalid(response)

    def test_remove_invalid_type_v6(self):
        mock = self.mock_network_v6()
        mock[self.XML_KEY][self.ATTR_KEY_IPS] = str(
            self.ID_NETWORK_IPV6_VALID) + '-' + self.LETTER_ATTR
        response = self.client_autenticado().putXML(self.URL_REMOVE, mock)
        self._attr_invalid(response)

    def test_remove_does_not_exist_v4(self):
        mock = self.mock_network_v4()
        mock[self.XML_KEY][self.ATTR_KEY_IPS] = str(
            self.ID_NONEXISTENT) + '-' + self.TYPE_NETWORK_V4
        response = self.client_autenticado().putXML(self.URL_REMOVE, mock)
        self._attr_invalid(response, CodeError.NETWORK_IPV4_NOT_FOUND)

    def test_remove_does_not_exist_v6(self):
        mock = self.mock_network_v6()
        mock[self.XML_KEY][self.ATTR_KEY_IPS] = str(
            self.ID_NONEXISTENT) + '-' + self.TYPE_NETWORK_V6
        response = self.client_autenticado().putXML(self.URL_REMOVE, mock)
        self._attr_invalid(response, CodeError.NETWORK_IPV6_NOT_FOUND)


class NetworkTest(NetworkConfigTest):

    def test_save_valid(self):
        mock = self.mock_network_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_save_no_permission(self):
        mock = self.mock_network_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_network_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_network_alter_valid()
        response = self.client_autenticado().postXML(
            self.URL_ALTER, {self.XML_KEY_ALTER: mock})
        valid_response(response)
        net = NetworkIPv4.get_by_pk(self.ID_NETWORK_IPV4_ALTER_VALID)
        self.valid_network_attr(mock, model_to_dict(net))

    def test_alter_no_permission(self):
        mock = self.mock_network_alter_valid()
        response = self.client_no_permission().postXML(
            self.URL_ALTER, {self.XML_KEY_ALTER: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_network_alter_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ALTER, {self.XML_KEY_ALTER: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv4_valid(self):
        mock = self.mock_network_ip_valid()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_NETWORK_IPV4, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_NETWORK_IP)

    def test_save_ipv4_no_permission(self):
        mock = self.mock_network_ip_valid()
        response = self.client_no_permission().postXML(
            self.URL_SAVE_NETWORK_IPV4, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv4_no_write_permission(self):
        mock = self.mock_network_ip_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_SAVE_NETWORK_IPV4, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv6_valid(self):
        mock = self.mock_network_ip_valid()
        mock['id_vlan'] = 17
        response = self.client_autenticado().postXML(
            self.URL_SAVE_NETWORK_IPV6, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_NETWORK_IP)

    def test_save_ipv6_no_permission(self):
        mock = self.mock_network_ip_valid()
        mock['id_vlan'] = 17
        response = self.client_no_permission().postXML(
            self.URL_SAVE_NETWORK_IPV6, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv6_no_write_permission(self):
        mock = self.mock_network_ip_valid()
        mock['id_vlan'] = 17
        response = self.client_no_write_permission().postXML(
            self.URL_SAVE_NETWORK_IPV6, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_networkIpv4_set_first_available_ip_valid(self):
        mock = self.mock_networkIpv4_set_first_available_ip_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        response_dict = valid_content(response, self.XML_KEY)

        response = self.client_autenticado().get(
            self.URL_GET_IPS_BY_IPV4_ID % response_dict['id'])
        valid_response(response)
        valid_content(response, self.XML_KEY_IPS_NETWORK, True)

    def test_save_networkIpv6_set_first_available_ip_valid(self):
        mock = self.mock_networkIpv6_set_first_available_ip_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        response_dict = valid_content(response, self.XML_KEY)

        response = self.client_autenticado().get(
            self.URL_GET_IPS_BY_IPV6_ID % response_dict['id'])
        valid_response(response)
        valid_content(response, self.XML_KEY_IPS_NETWORK, True)

    def test_save_networkIpv4AddResource_set_first_available_ip_valid(self):
        mock = self.mock_networkIpv4AddResource_set_first_available_ip_valid()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_NETWORK_IPV4, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        response_dict = valid_content(response, self.XML_KEY_NETWORK_IP)

        response = self.client_autenticado().get(
            self.URL_GET_IPS_BY_IPV4_ID % response_dict['id_network'])
        valid_response(response)
        valid_content(response, self.XML_KEY_IPS_NETWORK, True)

    def test_save_networkIpv6AddResource_set_first_available_ip_valid(self):
        mock = self.mock_networkIpv6AddResource_set_first_available_ip_valid()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_NETWORK_IPV6, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        response_dict = valid_content(response, self.XML_KEY_NETWORK_IP)

        response = self.client_autenticado().get(
            self.URL_GET_IPS_BY_IPV6_ID % response_dict['id_network'])
        valid_response(response)
        valid_content(response, self.XML_KEY_IPS_NETWORK, True)


class NetworkAttrNetworkTest(NetworkConfigTest, AttrTest):

    KEY_ATTR = "network"

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_save_invalid(self):
        mock = self.mock_network_valid()
        mock[self.KEY_ATTR] = string_generator(10)
        self.process_save_attr_invalid(mock)


class NetworkAttrIdNetworkTest(NetworkConfigTest, AttrTest):

    def test_alter_nonexistent(self):
        self.alter_network_attr_invalid(
            self.ID_NONEXISTENT, "id_network", CodeError.NETWORK_IPV4_NOT_FOUND)

    def test_alter_negative(self):
        self.alter_network_attr_invalid(self.NEGATIVE_ATTR, "id_network")

    def test_alter_letter(self):
        self.alter_network_attr_invalid(self.LETTER_ATTR, "id_network")

    def test_alter_zero(self):
        self.alter_network_attr_invalid(self.ZERO_ATTR, "id_network")

    def test_alter_empty(self):
        self.alter_network_attr_invalid(self.EMPTY_ATTR, "id_network")

    def test_alter_none(self):
        self.alter_network_attr_invalid(self.NONE_ATTR, "id_network")


class NetworkAttrIpTypeTest(NetworkConfigTest, AttrTest):

    def test_alter_nonexistent(self):
        self.alter_network_attr_invalid(self.ID_NONEXISTENT, "ip_type")

    def test_alter_negative(self):
        self.alter_network_attr_invalid(self.NEGATIVE_ATTR, "ip_type")

    def test_alter_letter(self):
        self.alter_network_attr_invalid(self.LETTER_ATTR, "ip_type")

    def test_alter_invalid(self):
        self.alter_network_attr_invalid(2, "ip_type")

    def test_alter_empty(self):
        self.alter_network_attr_invalid(self.EMPTY_ATTR, "ip_type")

    def test_alter_none(self):
        self.alter_network_attr_invalid(self.NONE_ATTR, "ip_type")


class NetworkAttrVlanTest(NetworkConfigTest, AttrTest):

    KEY_ATTR = "id_vlan"
    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_network_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_SAVE, {self.XML_KEY: mock})
        self._not_found(response)

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_save_ipv4_nonexistent(self):
        self.save_network_ip_attr_invalid(
            self.ID_NONEXISTENT, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4, self.CODE_ERROR_NOT_FOUND)

    def test_save_ipv4_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_empty(self):
        self.save_network_ip_attr_invalid(
            self.EMPTY_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_none(self):
        self.save_network_ip_attr_invalid(
            self.NONE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv6_nonexistent(self):
        self.save_network_ip_attr_invalid(
            self.ID_NONEXISTENT, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6, self.CODE_ERROR_NOT_FOUND)

    def test_save_ipv6_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_empty(self):
        self.save_network_ip_attr_invalid(
            self.EMPTY_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_none(self):
        self.save_network_ip_attr_invalid(
            self.NONE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)


class NetworkAttrNetworkTypeTest(NetworkConfigTest, AttrTest):

    KEY_ATTR = "id_network_type"
    CODE_ERROR_NOT_FOUND = CodeError.NETWORK_TYPE_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_network_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_SAVE, {self.XML_KEY: mock})
        self._not_found(response)

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_nonexistent(self):
        self.alter_network_attr_invalid(
            self.ID_NONEXISTENT, "id_net_type", self.CODE_ERROR_NOT_FOUND)

    def test_alter_negative(self):
        self.alter_network_attr_invalid(self.NEGATIVE_ATTR, "id_net_type")

    def test_alter_letter(self):
        self.alter_network_attr_invalid(self.LETTER_ATTR, "id_net_type")

    def test_alter_zero(self):
        self.alter_network_attr_invalid(self.ZERO_ATTR, "id_net_type")

    def test_alter_empty(self):
        self.alter_network_attr_invalid(self.EMPTY_ATTR, "id_net_type")

    def test_alter_none(self):
        self.alter_network_attr_invalid(self.NONE_ATTR, "id_net_type")

    def test_save_ipv4_nonexistent(self):
        self.save_network_ip_attr_invalid(
            self.ID_NONEXISTENT, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV4, self.CODE_ERROR_NOT_FOUND)

    def test_save_ipv4_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_empty(self):
        self.save_network_ip_attr_invalid(
            self.EMPTY_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_none(self):
        self.save_network_ip_attr_invalid(
            self.NONE_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv6_nonexistent(self):
        self.save_network_ip_attr_invalid(
            self.ID_NONEXISTENT, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV6, self.CODE_ERROR_NOT_FOUND)

    def test_save_ipv6_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_empty(self):
        self.save_network_ip_attr_invalid(
            self.EMPTY_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_none(self):
        self.save_network_ip_attr_invalid(
            self.NONE_ATTR, "id_tipo_rede", self.URL_SAVE_NETWORK_IPV6)


class NetworkAttrEnvironmentVipTest(NetworkConfigTest, AttrTest):

    KEY_ATTR = "id_environment_vip"
    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_network_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_SAVE, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_nonexistent(self):
        self.alter_network_attr_invalid(
            self.ID_NONEXISTENT, "id_env_vip", self.CODE_ERROR_NOT_FOUND)

    def test_alter_negative(self):
        self.alter_network_attr_invalid(self.NEGATIVE_ATTR, "id_env_vip")

    def test_alter_letter(self):
        self.alter_network_attr_invalid(self.LETTER_ATTR, "id_env_vip")

    def test_alter_zero(self):
        self.alter_network_attr_invalid(self.ZERO_ATTR, "id_env_vip")

    def test_save_ipv4_nonexistent(self):
        self.save_network_ip_attr_invalid(
            self.ID_NONEXISTENT, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV4, self.CODE_ERROR_NOT_FOUND)

    def test_save_ipv4_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv6_nonexistent(self):
        self.save_network_ip_attr_invalid(
            self.ID_NONEXISTENT, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV6, self.CODE_ERROR_NOT_FOUND)

    def test_save_ipv6_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, "id_ambiente_vip", self.URL_SAVE_NETWORK_IPV6)


class NetworkAttrPrefix(NetworkConfigTest, AttrTest):

    KEY_ATTR = "prefix"

    def test_save_ipv4_valid(self):
        mock = self.mock_network_ip_valid()
        mock[self.KEY_ATTR] = 26
        response = self.client_autenticado().postXML(
            self.URL_SAVE_NETWORK_IPV4, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_NETWORK_IP)

    def test_save_ipv4_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_greater_than_32(self):
        self.save_network_ip_attr_invalid(
            33, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv6_valid(self):
        mock = self.mock_network_ip_valid()
        mock[self.KEY_ATTR] = 65
        mock['id_vlan'] = 17
        response = self.client_autenticado().postXML(
            self.URL_SAVE_NETWORK_IPV6, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_NETWORK_IP)

    def test_save_ipv6_negative(self):
        self.save_network_ip_attr_invalid(
            self.NEGATIVE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_letter(self):
        self.save_network_ip_attr_invalid(
            self.LETTER_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_zero(self):
        self.save_network_ip_attr_invalid(
            self.ZERO_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_greater_than_128(self):
        self.save_network_ip_attr_invalid(
            129, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)


class NetworkHostsAttrNumHosts(NetworkConfigTest, AttrTest):

    KEY_ATTR = "num_hosts"

    def test_save_ipv4_valid(self):
        mock = self.mock_network_hosts_ip_valid()
        response = self.client_autenticado().putXML(
            self.URL_SAVE_NETWORK_IPV4, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_NETWORK_IP)

    def test_save_ipv4_none(self):
        self.save_network_hosts_ip_attr_invalid(
            self.NONE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_negative(self):
        self.save_network_hosts_ip_attr_invalid(
            self.NEGATIVE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_letter(self):
        self.save_network_hosts_ip_attr_invalid(
            self.LETTER_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_zero(self):
        self.save_network_hosts_ip_attr_invalid(
            self.ZERO_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv4_greater_than_max_ipv4_hosts(self):
        self.save_network_hosts_ip_attr_invalid(
            MAX_IPV4_HOSTS + 1, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV4)

    def test_save_ipv6_valid(self):
        mock = self.mock_network_hosts_ip_valid()
        mock['id_vlan'] = 17
        response = self.client_autenticado().putXML(
            self.URL_SAVE_NETWORK_IPV6, {self.XML_KEY_NETWORK_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_NETWORK_IP)

    def test_save_ipv6_none(self):
        self.save_network_hosts_ip_attr_invalid(
            self.NONE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_negative(self):
        self.save_network_hosts_ip_attr_invalid(
            self.NEGATIVE_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_letter(self):
        self.save_network_hosts_ip_attr_invalid(
            self.LETTER_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_zero(self):
        self.save_network_hosts_ip_attr_invalid(
            self.ZERO_ATTR, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)

    def test_save_ipv6_greater_than_max_ipv6_hosts(self):
        self.save_network_hosts_ip_attr_invalid(
            MAX_IPV6_HOSTS + 1, self.KEY_ATTR, self.URL_SAVE_NETWORK_IPV6)
