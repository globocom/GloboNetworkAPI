# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import httplib
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, string_generator


class VipRequestConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/requisicaovips/fixtures/initial_data.yaml']
    XML_KEY = "vip"

    ID_VALID = 1
    ID_VIP_TO_VALIDATE = 5
    ID_VIP_TO_CREATE = 6
    ID_VIP_ALREADY_CREATED = 7
    ID_VIP_TO_REMOVE_CREATED = 8
    ID_VIP_TO_DELETE = 91

    ID_VIP_TO_EDIT_REALS = 12

    ID_VIP_TO_ALTER = 14
    ID_VIP_TO_ALTER2 = 13

    ID_VIP_ALTER_HEALTHCHECK = 15
    ID_VIP_ALTER_PRIORITY = 16

    ID_VALID_VIP_TO_CHECK_REAL = 10
    ID_VALID_VIP_TO_ADD_REAL = 11
    ID_VALID_VIP_TO_ENABLE_REAL = 30
    ID_VALID_VIP_TO_REMOVE_REAL = 31

    ID_IPV4_TO_ADD_VIP = 33
    ID_IPV6_TO_ADD_VIP = 22

    ID_IPV4_TO_ALTER_VIP = 45
    ID_IPV4_TO_ALTER2_VIP = 43

    ID_EQUIP_VALID_REAL = 41
    ID_IPV4_TO_CHECK_REAL = 35
    ID_IPV4_TO_ADD_REAL = 38
    ID_IPV4_TO_ENABLE_REAL = 52

    ID_IPV6_TO_CHECK_REAL = 23
    ID_IPV6_TO_ADD_REAL = 24

    ID_IPV4_TO_REMOVE_REAL = 54
    ID_IPV6_TO_ENABLE_REAL = 40
    ID_IPV6_TO_REMOVE_REAL = 41

    ID_VALID_VIP_EDIT_MAXCON = 32
    MAXCON_VALID = 100

    URL_GET_ALL = '/vip/all/'
    URL_GET_BY_ID = '/requestvip/getbyid/%s/'
    URL_GET_BY_IPV4 = '/vip/ipv4/all/'
    URL_GET_BY_IPV6 = '/vip/ipv6/all/'
    URL_SEARCH = '/vip/%s/'
    URL_SEARCH_PAGINATE = '/requestvip/get_by_ip_id/'
    URL_VALIDATE = '/vip/validate/%s/'
    URL_CREATE_SCRIPT = '/vip/create/'
    URL_REMOVE_SCRIPT = '/vip/remove/'
    URL_DELETE = '/vip/delete/%s/'
    URL_ADD = '/requestvip/'
    URL_SCRIPT_REAL = '/vip/real/'
    URL_EDIT_REALS = '/vip/real/edit/'
    URL_ADD2 = '/vip/'
    URL_ALTER = '/requestvip/%s/'
    URL_ALTER2 = '/vip/%s/'
    URL_VALIDATE_REAL = '/vip/real/valid/'
    URL_EDIT_MAXCON = '/vip/%s/maxcon/%s/'
    URL_ALTER_HEALTHCHECK = '/vip/%s/healthcheck/'
    URL_ALTER_PRIORITY = '/vip/%s/priority/'
    URL_ADD_BLOCK = '/vip/add_block/%s/%s/%s/'
    URL_ADD_VIP_REQUEST = '/vip/'

    OBJ = RequisicaoVips

    def mock_to_get_by_ipv4(self):
        mock = {}
        mock['ipv4'] = '192.168.55.122'
        mock['all_prop'] = 0
        return mock

    def get_by_ipv4(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_get_by_ipv4()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_GET_BY_IPV4, {self.XML_KEY: mock})
        return response

    def mock_to_get_by_ipv6(self):
        mock = {}
        mock['ipv6'] = 'ffab:cdef:ffff:ffff:0000:0000:0000:0122'
        mock['all_prop'] = 0
        return mock

    def get_by_ipv6(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_get_by_ipv6()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_GET_BY_IPV6, {self.XML_KEY: mock})
        return response

    def mock_to_search_paginate(self):
        mock = {}
        mock["start_record"] = 0
        mock["end_record"] = 25
        mock["asorting_cols"] = None
        mock["searchable_columns"] = None
        mock["custom_search"] = None

        mock['id_vip'] = None
        mock['ip'] = None
        mock['create'] = None
        return mock

    def search_paginate(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_search_paginate()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_SEARCH_PAGINATE, {self.XML_KEY: mock})
        return response

    def mock_to_create_vip_script(self):
        mock = {}
        mock['id_vip'] = self.ID_VIP_TO_CREATE
        return mock

    def create_vip_script(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_create_vip_script()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_CREATE_SCRIPT, {self.XML_KEY: mock})
        return response

    def mock_to_remove_vip_script(self):
        mock = {}
        mock['id_vip'] = self.ID_VIP_TO_REMOVE_CREATED
        return mock

    def remove_vip_script(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_remove_vip_script()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_REMOVE_SCRIPT, {self.XML_KEY: mock})
        return response

    def mock_to_add_vip(self):
        mock = {}
        mock['id_ipv4'] = self.ID_IPV4_TO_ADD_VIP
        mock['id_ipv6'] = None
        mock['id_healthcheck_expect'] = 2
        mock['finalidade'] = 'Finality_TXT'
        mock['cliente'] = 'Client_TXT'
        mock['ambiente'] = 'PQuaQua_Environment_TXT'
        mock['cache'] = 'Cache'
        mock['maxcon'] = 10
        mock['metodo_bal'] = 'WEIGHTED'
        mock['persistencia'] = 'Persistence'
        mock['healthcheck_type'] = 'HTTP'
        mock['healthcheck'] = 'GET /Healthcheck/ HTTP/1.0'
        mock['timeout'] = '5 ms'
        mock['host'] = 'Host'
        mock['areanegocio'] = 'AreaNegocio'
        mock['nome_servico'] = 'NomeServico'
        mock['l7_filter'] = None
        mock['reals'] = {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.130',
                                   'port_vip': '800', 'id_ip': self.ID_IPV4_TO_ADD_VIP, 'port_real': '8080'}]}
        mock['reals_prioritys'] = {'reals_priority': [1]}
        mock['reals_weights'] = {'reals_weight': [1]}
        mock['portas_servicos'] = {'porta': ['80:8000']}
        return mock

    def add_vip(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_add_vip()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_ADD, {self.XML_KEY: mock})
        return response

    def add_vip_with_real_different_envs(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_add_vip_with_real_different_envs()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_ADD_VIP_REQUEST, {self.XML_KEY: mock})
        return response

    def mock_to_add_vip_with_real_different_envs(self):
        mock = {}
        mock['id_ip'] = 127
        mock['id_healthcheck_expect'] = 3
        mock['finalidade'] = 'VIP_FINALITY'
        mock['cliente'] = 'VIP_CLIENT'
        mock['ambiente'] = 'VIP_ENV'
        mock['cache'] = 'Cache'
        mock['maxcon'] = 10
        mock['metodo_bal'] = 'WEIGHTED'
        mock['persistencia'] = 'Persistence'
        mock['healthcheck_type'] = 'HTTP'
        mock['healthcheck'] = 'GET /Healthcheck/ HTTP/1.0'
        mock['timeout'] = '5 ms'
        mock['portas_servicos'] = {'porta': ['80:8000']}
        mock['reals'] = {
            'real': [{'real_name': 'EQUIPVIPTEST2', 'real_ip': '60.60.60.60'}]}
        mock['host'] = 'Host'
        mock['dsr'] = 'dsr'
        mock['bal_ativo'] = string_generator(10)
        mock['transbordos'] = {'transbordo': []}
        return mock

    def mock_to_check_real(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_CHECK_REAL
        mock['ip_id'] = self.ID_IPV4_TO_CHECK_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'chk'
        mock['network_version'] = 'v4'
        return mock

    def mock_to_check_real_ipv6(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_CHECK_REAL
        mock['ip_id'] = self.ID_IPV6_TO_CHECK_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'chk'
        mock['network_version'] = 'v6'
        return mock

    def mock_to_add_real(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_ADD_REAL
        mock['ip_id'] = self.ID_IPV4_TO_ADD_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'add'
        mock['network_version'] = 'v4'
        return mock

    def mock_to_add_real_ipv6(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_ADD_REAL
        mock['ip_id'] = self.ID_IPV6_TO_ADD_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'add'
        mock['network_version'] = 'v6'
        return mock

    def mock_to_enable_real(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_ENABLE_REAL
        mock['ip_id'] = self.ID_IPV4_TO_ENABLE_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'ena'
        mock['network_version'] = 'v4'
        return mock

    def mock_to_disable_real(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_ENABLE_REAL
        mock['ip_id'] = self.ID_IPV4_TO_ENABLE_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'dis'
        mock['network_version'] = 'v4'
        return mock

    def mock_to_enable_real_v6(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_ENABLE_REAL
        mock['ip_id'] = self.ID_IPV6_TO_ENABLE_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'ena'
        mock['network_version'] = 'v6'
        return mock

    def mock_to_disable_real_v6(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_ENABLE_REAL
        mock['ip_id'] = self.ID_IPV6_TO_ENABLE_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'dis'
        mock['network_version'] = 'v6'
        return mock

    def mock_to_remove_real(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_REMOVE_REAL
        mock['ip_id'] = self.ID_IPV4_TO_REMOVE_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'del'
        mock['network_version'] = 'v4'
        return mock

    def mock_to_remove_real_v6(self):
        mock = {}
        mock['vip_id'] = self.ID_VALID_VIP_TO_REMOVE_REAL
        mock['ip_id'] = self.ID_IPV6_TO_REMOVE_REAL
        mock['equip_id'] = self.ID_EQUIP_VALID_REAL
        mock['operation'] = 'del'
        mock['network_version'] = 'v6'
        return mock

    def mock_to_valid_real(self):
        mock = {}
        mock['ip'] = '192.168.55.150'
        mock['name_equipment'] = 'BALANCINGEQUIPFORVIP2'
        mock['id_environment_vip'] = 1
        return mock

    def mock_to_valid_real_v6(self):
        mock = {}
        mock['ip'] = 'ffab:cdef:ffff:ffff:0000:0000:0000:0142'
        mock['name_equipment'] = 'BALANCINGEQUIPFORVIP2'
        mock['id_environment_vip'] = 1
        return mock

    def script_real(self, mock, dicts=None, client=CLIENT_TYPES.TEST):
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_SCRIPT_REAL, {self.XML_KEY: mock})
        return response

    def mock_to_edit_reals(self):
        mock = {}
        mock['vip_id'] = self.ID_VIP_TO_EDIT_REALS
        mock['metodo_bal'] = 'WEIGHTED'
        mock['reals'] = {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.134', 'port_vip': '81', 'id_ip': self.ID_IPV4_TO_ADD_REAL, 'port_real': '80141'},
                                  {'real_name': 'BalancingEquipForVip2', 'real_ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:0125', 'port_vip': '81', 'id_ip': self.ID_IPV6_TO_ADD_REAL, 'port_real': '80142'}]}
        mock['reals_prioritys'] = {'reals_priority': [1, 2]}
        mock['reals_weights'] = {'reals_weight': [1, 2]}

        return mock

    def edit_reals(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_edit_reals()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).putXML(
            self.URL_EDIT_REALS, {self.XML_KEY: mock})
        return response

    def mock_to_add2_vip(self):
        mock = {}
        mock['id_ip'] = self.ID_IPV4_TO_ADD_VIP
        mock['id_healthcheck_expect'] = 2
        mock['finalidade'] = 'Finality_TXT'
        mock['cliente'] = 'Client_TXT'
        mock['ambiente'] = 'PQuaQua_Environment_TXT'
        mock['cache'] = 'Cache'
        mock['maxcon'] = 10
        mock['metodo_bal'] = 'WEIGHTED'
        mock['persistencia'] = 'Persistence'
        mock['healthcheck_type'] = 'HTTP'
        mock['healthcheck'] = 'GET /Healthcheck/ HTTP/1.0'
        mock['timeout'] = '5 ms'
        mock['portas_servicos'] = {'porta': ['80:8000']}
        mock['reals'] = {
            'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.130'}]}
        mock['host'] = 'Host'
        mock['dsr'] = 'dsr'
        mock['bal_ativo'] = string_generator(10)
        mock['transbordos'] = {'transbordo': []}
        return mock

    def add2_vip(self, dicts=None, client=CLIENT_TYPES.TEST):
        mock = self.mock_to_add2_vip()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).postXML(
            self.URL_ADD2, {self.XML_KEY: mock})
        return response

    def mock_to_alter_vip(self):
        mock = {}
        mock['validado'] = 0
        mock['vip_criado'] = 0
        mock['id_ipv4'] = self.ID_IPV4_TO_ALTER_VIP
        mock['id_ipv6'] = None
        mock['id_healthcheck_expect'] = 2
        mock['finalidade'] = 'Finality_TXT'
        mock['cliente'] = 'Client_TXT'
        mock['ambiente'] = 'PQuaQua_Environment_TXT'
        mock['cache'] = 'Cache'
        mock['maxcon'] = 10
        mock['metodo_bal'] = 'WEIGHTED'
        mock['persistencia'] = 'Persistence'
        mock['healthcheck_type'] = 'HTTP'
        mock['healthcheck'] = 'GET /Healthcheck/ HTTP/1.0'
        mock['timeout'] = '5 ms'
        mock['host'] = 'Host'
        mock['areanegocio'] = 'AreaNegocio'
        mock['nome_servico'] = 'NomeServico'
        mock['l7_filter'] = None
        mock['reals'] = {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.130',
                                   'port_vip': '80', 'id_ip': self.ID_IPV4_TO_ADD_VIP, 'port_real': '8090'}]}
        mock['reals_prioritys'] = {'reals_priority': [1]}
        mock['reals_weights'] = {'reals_weight': [1]}
        mock['portas_servicos'] = {'porta': ['80:8000']}
        return mock

    def alter_vip(self, dicts=None, client=CLIENT_TYPES.TEST, vip_id=ID_VIP_TO_ALTER):
        mock = self.mock_to_alter_vip()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).putXML(
            self.URL_ALTER % vip_id, {self.XML_KEY: mock})
        return response

    def mock_to_alter2_vip(self):
        mock = {}
        mock['id_ip'] = self.ID_IPV4_TO_ALTER2_VIP
        mock['id_healthcheck_expect'] = 2
        mock['validado'] = 0
        mock['vip_criado'] = 0
        mock['finalidade'] = 'Finality_TXT'
        mock['cliente'] = 'Client_TXT'
        mock['ambiente'] = 'PQuaQua_Environment_TXT'
        mock['cache'] = 'Cache'
        mock['maxcon'] = 10
        mock['metodo_bal'] = 'WEIGHTED'
        mock['persistencia'] = 'Persistence'
        mock['healthcheck_type'] = 'HTTP'
        mock['healthcheck'] = 'GET /Healthcheck/ HTTP/1.0'
        mock['timeout'] = '5 ms'
        mock['portas_servicos'] = {'porta': ['80:8000']}
        mock['reals'] = {'real': []}
        mock['host'] = 'Host'
        mock['dsr'] = 'dsr'
        mock['bal_ativo'] = string_generator(10)
        mock['transbordos'] = {'transbordo': []}
        mock['reals'] = {
            'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.130'}]}
        return mock

    def alter2_vip(self, dicts=None, client=CLIENT_TYPES.TEST, vip_id=ID_VIP_TO_ALTER2):
        mock = self.mock_to_alter2_vip()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).putXML(
            self.URL_ALTER2 % vip_id, {self.XML_KEY: mock})
        return response

    def mock_alter_healthcheck(self):
        mock = {}
        mock['healthcheck_type'] = 'HTTP'
        mock['healthcheck'] = 'GET /test/ HTTP/1.0'
        mock['id_healthcheck_expect'] = 2
        return mock

    def alter_healthcheck(self, dicts=None, client=CLIENT_TYPES.TEST, vip_id=ID_VIP_ALTER_HEALTHCHECK):
        mock = self.mock_alter_healthcheck()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).putXML(
            self.URL_ALTER_HEALTHCHECK % vip_id, {self.XML_KEY: mock})
        return response

    def mock_alter_priority(self):
        mock = {}
        mock['reals_prioritys'] = {'reals_priority': [2]}
        return mock

    def alter_priority(self, dicts=None, client=CLIENT_TYPES.TEST, vip_id=ID_VIP_ALTER_PRIORITY):
        mock = self.mock_alter_priority()
        if isinstance(dicts, dict):
            for (k, v) in dicts.iteritems():
                mock[k] = v
        response = self.switch(client).putXML(
            self.URL_ALTER_PRIORITY % vip_id, {self.XML_KEY: mock})
        return response


class VipRequestConsultationTest(VipRequestConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.VIP_REQUEST_NOT_FOUND

    def test_get_all_valid(self):
        response = self.client_autenticado().get(self.URL_GET_ALL)
        valid_response(response)
        content = valid_content(response)
        assert len(content.values()) >= 1

    def test_get_all_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_ALL)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_ALL)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_valid(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_id_no_permission(self):
        response = self.get_by_id(self.ID_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.get_by_id(
            self.ID_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
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

    def test_get_by_ipv4_valid(self):
        response = self.get_by_ipv4()
        valid_response(response)
        content = valid_content(response, 'ips')
        assert content['vips'] != None

    def test_get_by_ipv4_no_permission(self):
        response = self.get_by_ipv4(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ipv4_no_read_permission(self):
        response = self.get_by_ipv4(client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ipv4_all_prop_true(self):
        response = self.get_by_ipv4(dicts={'all_prop': True})
        self._attr_invalid(response)

    def test_get_by_ipv4_all_prop_false(self):
        response = self.get_by_ipv4(dicts={'all_prop': False})
        self._attr_invalid(response)

    def test_get_by_ipv4_all_prop_letter(self):
        response = self.get_by_ipv4(dicts={'all_prop': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv4_all_prop_empty(self):
        response = self.get_by_ipv4(dicts={'all_prop': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv4_no_read_none(self):
        response = self.get_by_ipv4(dicts={'all_prop': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv4_nonexistent(self):
        response = self.get_by_ipv4(dicts={'ipv4': '192.168.55.222'})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_get_by_ipv4_invalid_chars(self):
        response = self.get_by_ipv4(dicts={'ipv4': '192.168.55.1za'})
        self._attr_invalid(response)

    def test_get_by_ipv4_invalid_range(self):
        response = self.get_by_ipv4(dicts={'ipv4': '192.168.55.1122'})
        self._attr_invalid(response)

    def test_get_by_ipv4_invalid_comma(self):
        response = self.get_by_ipv4(dicts={'ipv4': '192,168,55,122'})
        self._attr_invalid(response)

    def test_get_by_ipv4_invalid_separators(self):
        response = self.get_by_ipv4(dicts={'ipv4': '192.168/55;122'})
        self._attr_invalid(response)

    def test_get_by_ipv6_valid(self):
        response = self.get_by_ipv6()
        valid_response(response)
        content = valid_content(response, 'ips')
        assert content['vips'] != None

    def test_get_by_ipv6_no_permission(self):
        response = self.get_by_ipv6(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ipv6_no_read_permission(self):
        response = self.get_by_ipv6(client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ipv6_all_prop_true(self):
        response = self.get_by_ipv6(dicts={'all_prop': True})
        self._attr_invalid(response)

    def test_get_by_ipv6_all_prop_false(self):
        response = self.get_by_ipv6(dicts={'all_prop': False})
        self._attr_invalid(response)

    def test_get_by_ipv6_all_prop_letter(self):
        response = self.get_by_ipv6(dicts={'all_prop': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv6_all_prop_empty(self):
        response = self.get_by_ipv6(dicts={'all_prop': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv6_no_read_none(self):
        response = self.get_by_ipv6(dicts={'all_prop': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_get_by_ipv6_nonexistent(self):
        response = self.get_by_ipv6(
            dicts={'ipv6': 'ffab:cdef:ffff:ffff:0000:0000:0000:2122'})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_get_by_ipv6_invalid_chars(self):
        response = self.get_by_ipv6(
            dicts={'ipv6': 'ffab:cdef:ffff:ffff:0000:0000:0000:uugd'})
        self._attr_invalid(response)

    def test_get_by_ipv6_invalid_range(self):
        response = self.get_by_ipv6(
            dicts={'ipv6': 'ffab:cdef:ffff:ffff:0000:0000:0000:90122'})
        self._attr_invalid(response)

    def test_get_by_ipv6_invalid_comma(self):
        response = self.get_by_ipv6(
            dicts={'ipv6': 'ffab,cdef,ffff,ffff,0000,0000,0000,0122'})
        self._attr_invalid(response)

    def test_get_by_ipv6_invalid_separators(self):
        response = self.get_by_ipv6(
            dicts={'ipv6': 'ffab:cdef/ffff.ffff;0000.0000.0000:0122'})
        self._attr_invalid(response)


class VipRequestValidateTest(VipRequestConfigTest, AttrTest):

    def test_validate_vip_valid(self):
        response = self.client_autenticado().get(
            self.URL_VALIDATE % self.ID_VIP_TO_VALIDATE)
        valid_response(response)

    def test_validate_vip_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_VALIDATE % self.ID_VIP_TO_VALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_validate_vip_no_write_permission(self):
        response = self.client_no_write_permission().get(
            self.URL_VALIDATE % self.ID_VIP_TO_VALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_validate_vip_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_VALIDATE % self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_validate_vip_letter(self):
        response = self.client_autenticado().get(
            self.URL_VALIDATE % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_validate_vip_zero(self):
        response = self.client_autenticado().get(
            self.URL_VALIDATE % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_validate_vip_negative(self):
        response = self.client_autenticado().get(
            self.URL_VALIDATE % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_validate_vip_empty(self):
        response = self.client_autenticado().get(
            self.URL_VALIDATE % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_validate_vip_none(self):
        response = self.client_autenticado().get(
            self.URL_VALIDATE % self.NONE_ATTR)
        self._attr_invalid(response)


class VipRequestCreateScriptTest(VipRequestConfigTest, AttrTest):

    def test_create_vip_valid(self):
        response = self.create_vip_script()
        valid_response(response)

    def test_create_vip_no_permission(self):
        response = self.create_vip_script(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_vip_no_write_permission(self):
        response = self.create_vip_script(
            client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_vip_not_validated(self):
        # ID_VALID_VIP_TO_CHECK_REAL isn't validated
        response = self.create_vip_script(
            {'id_vip': self.ID_VALID_VIP_TO_CHECK_REAL})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_YET_VALIDATED)

    def test_create_vip_already_created(self):
        response = self.create_vip_script(
            {'id_vip': self.ID_VIP_ALREADY_CREATED})
        self._attr_invalid(response, CodeError.VIP_REQUEST_ALREADY_CREATED)

    def test_create_vip_nonexistent(self):
        response = self.create_vip_script({'id_vip': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_create_vip_letter(self):
        response = self.create_vip_script({'id_vip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_create_vip_zero(self):
        response = self.create_vip_script({'id_vip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_create_vip_negative(self):
        response = self.create_vip_script({'id_vip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_create_vip_empty(self):
        response = self.create_vip_script({'id_vip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_create_vip_none(self):
        response = self.create_vip_script({'id_vip': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestRemoveScriptTest(VipRequestConfigTest, AttrTest):

    def test_remove_vip_valid(self):
        response = self.remove_vip_script()
        valid_response(response)

    def test_remove_vip_no_permission(self):
        response = self.remove_vip_script(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_vip_no_write_permission(self):
        response = self.remove_vip_script(
            client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_vip_not_validated(self):
        # ID_VALID_VIP_TO_CHECK_REAL isn't validated
        response = self.remove_vip_script(
            {'id_vip': self.ID_VALID_VIP_TO_CHECK_REAL})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_YET_VALIDATED)

    def test_remove_vip_not_created(self):
        response = self.remove_vip_script({'id_vip': self.ID_VIP_TO_CREATE})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_CREATED)

    def test_remove_vip_nonexistent(self):
        response = self.remove_vip_script({'id_vip': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_remove_vip_letter(self):
        response = self.remove_vip_script({'id_vip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_remove_vip_zero(self):
        response = self.remove_vip_script({'id_vip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_remove_vip_negative(self):
        response = self.remove_vip_script({'id_vip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_remove_vip_empty(self):
        response = self.remove_vip_script({'id_vip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_remove_vip_none(self):
        response = self.remove_vip_script({'id_vip': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestRemoveTest(VipRequestConfigTest, RemoveTest):

    URL_REMOVE = VipRequestConfigTest.URL_DELETE
    CODE_ERROR_NOT_FOUND = CodeError.VIP_REQUEST_NOT_FOUND

    def test_remove_valid(self):
        response = self.client_autenticado().delete(
            self.URL_DELETE % self.ID_VIP_TO_DELETE)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_DELETE % self.ID_VIP_TO_DELETE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_DELETE % self.ID_VIP_TO_DELETE)
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


class VipRequestAddTest(VipRequestConfigTest, AttrTest):

    def test_vip_add_valid(self):
        response = self.add_vip()
        valid_response(response)
        content = valid_content(response, 'requisicao_vip')

        # Remove so it does not stay in database
        self.client_autenticado().delete(self.URL_DELETE % content['id'])

    def test_vip_add_real_different_envs(self):
        response = self.add_vip_with_real_different_envs()
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_vip_add_ipv6_valid(self):
        response = self.add_vip()
        valid_response(response)
        content = valid_content(response, 'requisicao_vip')

        # Remove so it does not stay in database
        self.client_autenticado().delete(self.URL_DELETE % content['id'])

    def test_vip_add_no_permission(self):
        response = self.add_vip(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_add_no_write_permission(self):
        response = self.add_vip(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    # Invalid ipv4 id
    def test_vip_add_ipv4_nonexistent(self):
        response = self.add_vip(dicts={'id_ipv4': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_vip_add_ipv4_negative(self):
        response = self.add_vip(dicts={'id_ipv4': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv4_letter(self):
        response = self.add_vip(dicts={'id_ipv4': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv4_empty(self):
        response = self.add_vip(dicts={'id_ipv4': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv4_none(self):
        response = self.add_vip(dicts={'id_ipv4': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv4_zero(self):
        response = self.add_vip(dicts={'id_ipv4': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid ipv6 id
    def test_vip_add_ipv6_nonexistent(self):
        response = self.add_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_vip_add_ipv6_negative(self):
        response = self.add_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv6_letter(self):
        response = self.add_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv6_empty(self):
        response = self.add_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv6_none(self):
        response = self.add_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ipv6_zero(self):
        response = self.add_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid id_healthcheck_expect

    def test_vip_add_healthcheck_expect_nonexistent(self):
        response = self.add_vip(
            dicts={'id_healthcheck_expect': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.HEALTHCHECKEXPECT_NOT_FOUND)

    def test_vip_add_healthcheck_expect_negative(self):
        response = self.add_vip(
            dicts={'id_healthcheck_expect': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_healthcheck_expect_letter(self):
        response = self.add_vip(
            dicts={'id_healthcheck_expect': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_healthcheck_expect_empty(self):
        response = self.add_vip(
            dicts={'id_healthcheck_expect': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_expect_none(self):
        response = self.add_vip(
            dicts={'id_healthcheck_expect': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_expect_zero(self):
        response = self.add_vip(
            dicts={'id_healthcheck_expect': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid vip environment
    def test_vip_add_finality_nonexistent(self):
        response = self.add_vip(dicts={'finalidade': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_finality_none(self):
        response = self.add_vip(dicts={'finalidade': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_finality_empty(self):
        response = self.add_vip(dicts={'finalidade': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_finality_minsize(self):
        response = self.add_vip(dicts={'finalidade': string_generator(2)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_finality_maxsize(self):
        response = self.add_vip(dicts={'finalidade': string_generator(51)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_client_nonexistent(self):
        response = self.add_vip(dicts={'cliente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_client_none(self):
        response = self.add_vip(dicts={'cliente': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_client_empty(self):
        response = self.add_vip(dicts={'cliente': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_client_minsize(self):
        response = self.add_vip(dicts={'cliente': string_generator(2)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_client_maxsize(self):
        response = self.add_vip(dicts={'cliente': string_generator(51)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_p44_environment_nonexistent(self):
        response = self.add_vip(dicts={'ambiente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_p44_environment_none(self):
        response = self.add_vip(dicts={'ambiente': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_p44_environment_empty(self):
        response = self.add_vip(dicts={'ambiente': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_p44_environment_minsize(self):
        response = self.add_vip(dicts={'ambiente': string_generator(2)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_p44_environment_maxsize(self):
        response = self.add_vip(dicts={'ambiente': string_generator(51)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    # Invalid cache

    def test_vip_add_cache_nonexistent(self):
        response = self.add_vip(dicts={'cache': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_minsize(self):
        response = self.add_vip(dicts={'cache': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_maxsize(self):
        response = self.add_vip(dicts={'cache': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_empty(self):
        response = self.add_vip(dicts={'cache': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_none(self):
        response = self.add_vip(dicts={'cache': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    # Invalid maxcon
    def test_vip_add_maxcon_negative(self):
        response = self.add_vip(dicts={'maxcon': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_maxcon_letter(self):
        response = self.add_vip(dicts={'maxcon': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_maxcon_empty(self):
        response = self.add_vip(dicts={'maxcon': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_maxcon_none(self):
        response = self.add_vip(dicts={'maxcon': self.NONE_ATTR})
        self._attr_invalid(response)

    # Invalid balancing method
    def test_vip_add_bal_method_nonexistent(self):
        response = self.add_vip(dicts={'metodo_bal': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_minsize(self):
        response = self.add_vip(dicts={'metodo_bal': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_maxsize(self):
        response = self.add_vip(dicts={'metodo_bal': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_empty(self):
        response = self.add_vip(dicts={'metodo_bal': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_none(self):
        response = self.add_vip(dicts={'metodo_bal': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    # Invalid persistence
    def test_vip_add_persistence_nonexistent(self):
        response = self.add_vip(dicts={'persistencia': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_minsize(self):
        response = self.add_vip(dicts={'persistencia': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_maxsize(self):
        response = self.add_vip(dicts={'persistencia': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_empty(self):
        response = self.add_vip(dicts={'persistencia': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_none(self):
        response = self.add_vip(dicts={'persistencia': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    # Invalid healthcheck_type
    def test_vip_add_healthcheck_type_nonexistent(self):
        response = self.add_vip(
            dicts={'healthcheck_type': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_add_healthcheck_type_empty(self):
        response = self.add_vip(dicts={'healthcheck_type': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_add_healthcheck_type_none(self):
        response = self.add_vip(dicts={'healthcheck_type': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    # Invalid healthcheck URL
    def test_vip_add_healthcheck_empty(self):
        response = self.add_vip(dicts={'healthcheck': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_none(self):
        response = self.add_vip(dicts={'healthcheck': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_invalid_tcp(self):
        response = self.add_vip(
            dicts={'healthcheck_type': 'TCP', 'id_healthcheck_expect': self.NONE_ATTR, 'healthcheck': string_generator(10)})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_NOT_HTTP_NOT_NONE)

    # Invalid timeout
    def test_vip_add_timeout_nonexistent(self):
        response = self.add_vip(dicts={'timeout': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_minsize(self):
        response = self.add_vip(dicts={'timeout': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_maxsize(self):
        response = self.add_vip(dicts={'timeout': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_empty(self):
        response = self.add_vip(dicts={'timeout': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_none(self):
        response = self.add_vip(dicts={'timeout': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    # Invalid service ports
    def test_vip_add_service_ports_invalid_first(self):
        response = self.add_vip(
            dicts={'portas_servicos': {'porta': ['njk:8000']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_invalid_second(self):
        response = self.add_vip(
            dicts={'portas_servicos': {'porta': ['80:---m']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_empty_first(self):
        response = self.add_vip(
            dicts={'portas_servicos': {'porta': [':8000']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_empty_second(self):
        response = self.add_vip(dicts={'portas_servicos': {'porta': ['80:']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_no_dict_entry(self):
        response = self.add_vip(dicts={'portas_servicos': {}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_none(self):
        response = self.add_vip(
            dicts={'portas_servicos': {'porta': self.NONE_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)

    def test_vip_add_service_ports_empty(self):
        response = self.add_vip(
            dicts={'portas_servicos': {'porta': self.EMPTY_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)

    # Invalid reals
    def test_vip_add_reals_none(self):
        response = self.add_vip(dicts={'reals': {'real': self.NONE_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_add_reals_empty(self):
        response = self.add_vip(dicts={'reals': {'real': self.EMPTY_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_add_reals_invalid_equip(self):
        response = self.add_vip(dicts={'reals': {
                                'real': [{'real_name': string_generator(10), 'real_ip': '192.168.55.130'}]}})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_add_reals_invalid_ip(self):
        response = self.add_vip(dicts={'reals': {'real': [
                                {'real_name': 'BalancingEquipForVip2', 'real_ip': string_generator(10)}]}})
        self._attr_invalid(response)

    def test_vip_add_reals_no_equip(self):
        response = self.add_vip(
            dicts={'reals': {'real': [{'real_ip': '192.168.55.130'}]}})
        self._attr_invalid(response)

    def test_vip_add_reals_no_ip(self):
        response = self.add_vip(
            dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2'}]}})
        self._attr_invalid(response)

    # Invalid reals priorities
    def test_vip_add_reals_priority_no_dict_entry(self):
        response = self.add_vip(dicts={'reals_prioritys': {}})
        self._attr_invalid(response)

    def test_vip_add_reals_priority_none(self):
        response = self.add_vip(
            dicts={'reals_prioritys': {'reals_priority': self.NONE_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_add_reals_priority_empty(self):
        response = self.add_vip(
            dicts={'reals_prioritys': {'reals_priority': self.EMPTY_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_add_reals_priority_letter(self):
        response = self.add_vip(
            dicts={'reals_prioritys': {'reals_priority': [self.LETTER_ATTR]}})
        self._attr_invalid(response)

    def test_vip_add_reals_priority_negative(self):
        response = self.add_vip(
            dicts={'reals_prioritys': {'reals_priority': [self.NEGATIVE_ATTR]}})
        self._attr_invalid(response)

    def test_vip_add_reals_priority_wrong_number(self):
        response = self.add_vip(
            dicts={'reals_prioritys': {'reals_priority': [1, 2]}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    # Invalid reals weights
    def test_vip_add_reals_weight_no_dict_entry(self):
        response = self.add_vip(dicts={'reals_weights': {}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    def test_vip_add_reals_weight_none(self):
        response = self.add_vip(
            dicts={'reals_weights': {'reals_weight': self.NONE_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    def test_vip_add_reals_weight_empty(self):
        response = self.add_vip(
            dicts={'reals_weights': {'reals_weight': self.EMPTY_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    def test_vip_add_reals_weight_letter(self):
        response = self.add_vip(
            dicts={'reals_weights': {'reals_weight': [self.LETTER_ATTR]}})
        self._attr_invalid(response)

    def test_vip_add_reals_weight_negative(self):
        response = self.add_vip(
            dicts={'reals_weights': {'reals_weight': [self.NEGATIVE_ATTR]}})
        self._attr_invalid(response)

    def test_vip_add_reals_weight_wrong_number(self):
        response = self.add_vip(
            dicts={'reals_weights': {'reals_weight': [1, 2]}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    # RULE

    def test_vip_add_rule_invalid(self):
        response = self.add_vip(dicts={'rule_id': 123})
        self._attr_invalid(response, CodeError.RULE_NOT_FIND)

    def test_vip_add_rule_letter(self):
        response = self.add_vip(dicts={'rule_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_rule_negative(self):
        response = self.add_vip(dicts={'rule_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_rule_zero(self):
        response = self.add_vip(dicts={'rule_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Hosts

    def test_vip_add_host_none(self):
        response = self.add_vip(dicts={'host': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_host_empty(self):
        response = self.add_vip(dicts={'host': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_host_minsize_3(self):
        response = self.add_vip(dicts={'host': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_add_host_maxsize_100(self):
        response = self.add_vip(dicts={'host': string_generator(101)})
        self._attr_invalid(response)

    # Areanegocio

    def test_vip_add_areanegocio_none(self):
        response = self.add_vip(dicts={'areanegocio': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_areanegocio_empty(self):
        response = self.add_vip(dicts={'areanegocio': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_areanegocio_minsize_3(self):
        response = self.add_vip(dicts={'areanegocio': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_add_areanegocio_maxsize_100(self):
        response = self.add_vip(dicts={'areanegocio': string_generator(101)})
        self._attr_invalid(response)

    # Nome servico

    def test_vip_add_nome_servico_none(self):
        response = self.add_vip(dicts={'nome_servico': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_nome_servico_empty(self):
        response = self.add_vip(dicts={'nome_servico': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_nome_servico_minsize_3(self):
        response = self.add_vip(dicts={'nome_servico': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_add_nome_servico_maxsize_100(self):
        response = self.add_vip(dicts={'nome_servico': string_generator(101)})
        self._attr_invalid(response)


class VipRequestCheckRealsTest(VipRequestConfigTest, AttrTest):

    def test_vip_check_real_valid(self):
        response = self.script_real(mock=self.mock_to_check_real())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_check_real_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_check_real_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_check_real_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_check_real_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_check_real_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_check_real_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_check_real_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_network_version_invalid(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_check_real_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestCheckRealsIpv6Test(VipRequestConfigTest, AttrTest):

    def test_vip_check_real_valid(self):
        response = self.script_real(mock=self.mock_to_check_real_ipv6())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_check_real_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_check_real_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_check_real_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_check_real_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_check_real_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_check_real_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_check_real_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_network_version_invalid(self):
        response = self.script_real(mock=self.mock_to_check_real_ipv6(), dicts={
                                    'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_check_real_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_check_real_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_check_real_ipv6(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestAddRealsTest(VipRequestConfigTest, AttrTest):

    def test_vip_add_real_valid(self):
        response = self.script_real(mock=self.mock_to_add_real())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_add_real_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_add_real_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_add_real_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_add_real_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_add_real_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_add_real_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_add_real_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_network_version_invalid(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_add_real_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestAddRealsIpv6Test(VipRequestConfigTest, AttrTest):

    def test_vip_add_real_valid(self):
        response = self.script_real(mock=self.mock_to_add_real_ipv6())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_add_real_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_add_real_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_add_real_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_add_real_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_add_real_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_add_real_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_add_real_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_network_version_invalid(self):
        response = self.script_real(mock=self.mock_to_add_real_ipv6(), dicts={
                                    'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_add_real_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_real_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_add_real_ipv6(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestEditRealsTest(VipRequestConfigTest, AttrTest):

    def test_a_for_first_vip_edit_reals_valid_no_changes(self):
        response = self.edit_reals()
        valid_response(response)

    def test_vip_edit_reals_no_permission(self):
        response = self.edit_reals(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_edit_reals_no_write_permission(self):
        response = self.edit_reals(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_edit_reals_valid_add_new_real(self):
        response = self.edit_reals(dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.136', 'port_vip': '81', 'id_ip': self.ID_IPV4_TO_ADD_REAL, 'port_real': '8099'},
                                                             {'real_name': 'BalancingEquipForVip2', 'real_ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:0126',
                                                                 'port_vip': '81', 'id_ip': self.ID_IPV6_TO_ADD_REAL, 'port_real': '8591'},
                                                             {'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.137', 'port_vip': '81', 'id_ip': self.ID_IPV4_TO_ADD_REAL, 'port_real': '8191'}]},
                                          'reals_prioritys': {'reals_priority': [1, 2, 3]},
                                          'reals_weights': {'reals_weight': [1, 2, 3]}})
        valid_response(response)
        # Edit it back to default state
        response = self.edit_reals()

    def test_vip_edit_reals_add_new_wrong_priority(self):
        response = self.edit_reals(dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.136'},
                                                             {'real_name': 'BalancingEquipForVip2', 'real_ip':
                                                                 'ffab:cdef:ffff:ffff:0000:0000:0000:0126'},
                                                             {'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.137'}]},
                                          'reals_prioritys': {'reals_priority': [1, 3]},
                                          'reals_weights': {'reals_weight': [1, 2, 3]}})
        self._attr_invalid(
            response, CodeError.VIP_EDIT_REALS_PRIORITY_INCONSISTENCY)

    def test_vip_edit_reals_add_new_wrong_weights(self):
        response = self.edit_reals(dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.136'},
                                                             {'real_name': 'BalancingEquipForVip2', 'real_ip':
                                                                 'ffab:cdef:ffff:ffff:0000:0000:0000:0126'},
                                                             {'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.137'}]},
                                          'reals_prioritys': {'reals_priority': [1, 2, 3]},
                                          'reals_weights': {'reals_weight': [1, 2]}})
        self._attr_invalid(
            response, CodeError.VIP_EDIT_REALS_WEIGHT_INCONSISTENCY)

    def test_vip_edit_reals_valid_remove_real(self):
        response = self.edit_reals(dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.136', 'port_vip': '81', 'id_ip': self.ID_IPV4_TO_ADD_REAL, 'port_real': '8090'}]},
                                          'reals_prioritys': {'reals_priority': [1]},
                                          'reals_weights': {'reals_weight': [1]}})
        valid_response(response)
        # Edit it back to default state
        response = self.edit_reals()

    def test_vip_edit_reals_remove_real_wrong_priority(self):
        response = self.edit_reals(dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.136'}]},
                                          'reals_prioritys': {'reals_priority': [1, 2]},
                                          'reals_weights': {'reals_weight': [1]}})
        self._attr_invalid(
            response, CodeError.VIP_EDIT_REALS_PRIORITY_INCONSISTENCY)

    def test_vip_edit_reals_remove_real_wrong_weights(self):
        response = self.edit_reals(dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.136'}]},
                                          'reals_prioritys': {'reals_priority': [1]},
                                          'reals_weights': {'reals_weight': [1, 3]}})
        self._attr_invalid(
            response, CodeError.VIP_EDIT_REALS_WEIGHT_INCONSISTENCY)

    def test_vip_edit_reals_valid_add_remove_real(self):
        response = self.edit_reals(dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2', 'real_ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:0126', 'port_vip': '81', 'id_ip': self.ID_IPV6_TO_ADD_REAL, 'port_real': '8001'},
                                                             {'real_name': 'BalancingEquipForVip2', 'real_ip': '192.168.55.137', 'port_vip': '81', 'id_ip': self.ID_IPV4_TO_ADD_REAL, 'port_real': '8091'}]},
                                          'reals_prioritys': {'reals_priority': [1, 3]},
                                          'reals_weights': {'reals_weight': [1, 3]}})
        valid_response(response)
        # Edit it back to default state
        response = self.edit_reals()

    def test_vip_edit_reals_vip_nonexistent(self):
        response = self.edit_reals(dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_edit_reals_vip_letter(self):
        response = self.edit_reals(dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_edit_reals_vip_zero(self):
        response = self.edit_reals(dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_edit_reals_vip_negative(self):
        response = self.edit_reals(dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_edit_reals_vip_empty(self):
        response = self.edit_reals(dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_edit_reals_vip_none(self):
        response = self.edit_reals(dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestAdd2Test(VipRequestConfigTest, AttrTest):

    def test_vip_add2_valid(self):
        response = self.add2_vip()
        valid_response(response)
        content = valid_content(response, 'requisicao_vip')

        # Remove so it does not stay in database
        self.client_autenticado().delete(self.URL_DELETE % content['id'])

    def test_vip_add_no_permission(self):
        response = self.add2_vip(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_add_no_write_permission(self):
        response = self.add2_vip(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    # Invalid ip id
    def test_vip_add_ip_nonexistent(self):
        response = self.add2_vip(dicts={'id_ip': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_vip_add_ip_negative(self):
        response = self.add2_vip(dicts={'id_ip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ip_letter(self):
        response = self.add2_vip(dicts={'id_ip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ip_empty(self):
        response = self.add2_vip(dicts={'id_ip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ip_none(self):
        response = self.add2_vip(dicts={'id_ip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_ip_zero(self):
        response = self.add2_vip(dicts={'id_ip': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid id_healthcheck_expect
    def test_vip_add_healthcheck_expect_nonexistent(self):
        response = self.add2_vip(
            dicts={'id_healthcheck_expect': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.HEALTHCHECKEXPECT_NOT_FOUND)

    def test_vip_add_healthcheck_expect_negative(self):
        response = self.add2_vip(
            dicts={'id_healthcheck_expect': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_healthcheck_expect_letter(self):
        response = self.add2_vip(
            dicts={'id_healthcheck_expect': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_healthcheck_expect_empty(self):
        response = self.add2_vip(
            dicts={'id_healthcheck_expect': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_expect_none(self):
        response = self.add2_vip(
            dicts={'id_healthcheck_expect': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_expect_zero(self):
        response = self.add2_vip(
            dicts={'id_healthcheck_expect': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid vip environment
    def test_vip_add_finality_nonexistent(self):
        response = self.add2_vip(dicts={'finalidade': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_finality_none(self):
        response = self.add2_vip(dicts={'finalidade': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_finality_empty(self):
        response = self.add2_vip(dicts={'finalidade': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_finality_minsize(self):
        response = self.add2_vip(dicts={'finalidade': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_add_finality_maxsize(self):
        response = self.add2_vip(dicts={'finalidade': string_generator(51)})
        self._attr_invalid(response)

    def test_vip_add_client_nonexistent(self):
        response = self.add2_vip(dicts={'cliente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_client_none(self):
        response = self.add2_vip(dicts={'cliente': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_client_empty(self):
        response = self.add2_vip(dicts={'cliente': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_client_minsize(self):
        response = self.add2_vip(dicts={'cliente': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_add_client_maxsize(self):
        response = self.add2_vip(dicts={'cliente': string_generator(51)})
        self._attr_invalid(response)

    def test_vip_add_p44_environment_nonexistent(self):
        response = self.add2_vip(dicts={'ambiente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_add_p44_environment_none(self):
        response = self.add2_vip(dicts={'ambiente': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_p44_environment_empty(self):
        response = self.add2_vip(dicts={'ambiente': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_p44_environment_minsize(self):
        response = self.add2_vip(dicts={'ambiente': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_add_p44_environment_maxsize(self):
        response = self.add2_vip(dicts={'ambiente': string_generator(51)})
        self._attr_invalid(response)

    # Invalid cache
    def test_vip_add_cache_nonexistent(self):
        response = self.add2_vip(dicts={'cache': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_minsize(self):
        response = self.add2_vip(dicts={'cache': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_maxsize(self):
        response = self.add2_vip(dicts={'cache': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_empty(self):
        response = self.add2_vip(dicts={'cache': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_add_cache_none(self):
        response = self.add2_vip(dicts={'cache': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    # Invalid maxcon
    def test_vip_add_maxcon_negative(self):
        response = self.add2_vip(dicts={'maxcon': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_maxcon_letter(self):
        response = self.add2_vip(dicts={'maxcon': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_maxcon_empty(self):
        response = self.add2_vip(dicts={'maxcon': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_add_maxcon_none(self):
        response = self.add2_vip(dicts={'maxcon': self.NONE_ATTR})
        self._attr_invalid(response)

    # Invalid balancing method
    def test_vip_add_bal_method_nonexistent(self):
        response = self.add2_vip(dicts={'metodo_bal': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_minsize(self):
        response = self.add2_vip(dicts={'metodo_bal': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_maxsize(self):
        response = self.add2_vip(dicts={'metodo_bal': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_empty(self):
        response = self.add2_vip(dicts={'metodo_bal': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_add_bal_method_none(self):
        response = self.add2_vip(dicts={'metodo_bal': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    # Invalid persistence
    def test_vip_add_persistence_nonexistent(self):
        response = self.add2_vip(dicts={'persistencia': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_minsize(self):
        response = self.add2_vip(dicts={'persistencia': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_maxsize(self):
        response = self.add2_vip(dicts={'persistencia': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_empty(self):
        response = self.add2_vip(dicts={'persistencia': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_add_persistence_none(self):
        response = self.add2_vip(dicts={'persistencia': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    # Invalid healthcheck_type
    def test_vip_add_healthcheck_type_nonexistent(self):
        response = self.add2_vip(
            dicts={'healthcheck_type': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_add_healthcheck_type_empty(self):
        response = self.add2_vip(dicts={'healthcheck_type': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_add_healthcheck_type_none(self):
        response = self.add2_vip(dicts={'healthcheck_type': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    # Invalid healthcheck URL
    def test_vip_add_healthcheck_empty(self):
        response = self.add2_vip(dicts={'healthcheck': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_none(self):
        response = self.add2_vip(dicts={'healthcheck': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_add_healthcheck_invalid_tcp(self):
        response = self.add2_vip(
            dicts={'healthcheck_type': 'TCP', 'id_healthcheck_expect': self.NONE_ATTR, 'healthcheck': string_generator(10)})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_NOT_HTTP_NOT_NONE)

    # Invalid timeout
    def test_vip_add_timeout_nonexistent(self):
        response = self.add2_vip(dicts={'timeout': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_minsize(self):
        response = self.add2_vip(dicts={'timeout': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_maxsize(self):
        response = self.add2_vip(dicts={'timeout': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_empty(self):
        response = self.add2_vip(dicts={'timeout': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_add_timeout_none(self):
        response = self.add2_vip(dicts={'timeout': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    # Invalid service ports
    def test_vip_add_service_ports_invalid_first(self):
        response = self.add2_vip(
            dicts={'portas_servicos': {'porta': ['njk:8000']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_invalid_second(self):
        response = self.add2_vip(
            dicts={'portas_servicos': {'porta': ['80:---m']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_empty_first(self):
        response = self.add2_vip(
            dicts={'portas_servicos': {'porta': [':8000']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_empty_second(self):
        response = self.add2_vip(dicts={'portas_servicos': {'porta': ['80:']}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_no_dict_entry(self):
        response = self.add2_vip(dicts={'portas_servicos': {}})
        self._attr_invalid(response)

    def test_vip_add_service_ports_none(self):
        response = self.add2_vip(
            dicts={'portas_servicos': {'porta': self.NONE_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)

    def test_vip_add_service_ports_empty(self):
        response = self.add2_vip(
            dicts={'portas_servicos': {'porta': self.EMPTY_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)

    # Invalid reals
    def test_vip_add_reals_none(self):
        response = self.add2_vip(dicts={'reals': {'real': self.NONE_ATTR}})
        valid_response(response)

    def test_vip_add_reals_empty(self):
        response = self.add2_vip(dicts={'reals': {'real': self.EMPTY_ATTR}})
        # self._attr_invalid(response, CodeError.VIP_OLD_INVALID_REALS)
        valid_response(response)

    def test_vip_add_reals_no_equip(self):
        response = self.add2_vip(
            dicts={'reals': {'real': [{'real_ip': '192.168.55.130'}]}})
        self._attr_invalid(response)

    def test_vip_add_reals_no_ip(self):
        response = self.add2_vip(
            dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2'}]}})
        self._attr_invalid(response)
        # valid_response(response)


class VipRequestAlterTest(VipRequestConfigTest, AttrTest):

    def test_vip_alter_valid(self):
        response = self.alter_vip()
        valid_response(response)

    def test_vip_alter_ipv6_valid(self):
        response = self.alter_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.ID_IPV6_TO_ADD_VIP})
        valid_response(response)

    def test_vip_alter_no_permission(self):
        response = self.alter_vip(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_alter_no_write_permission(self):
        response = self.alter_vip(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    # vip id
    def test_vip_alter_id_negative(self):
        response = self.alter_vip(vip_id=self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_zero(self):
        response = self.alter_vip(vip_id=self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_letter(self):
        response = self.alter_vip(vip_id=self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_nonexistent(self):
        response = self.alter_vip(vip_id=self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_alter_id_none(self):
        response = self.alter_vip(vip_id=self.NONE_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_empty(self):
        response = self.alter_vip(vip_id=self.EMPTY_ATTR)
        self._attr_invalid(response)

    # Invalid ipv4 id
    def test_vip_alter_ipv4_nonexistent(self):
        response = self.alter_vip(dicts={'id_ipv4': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_vip_alter_ipv4_negative(self):
        response = self.alter_vip(dicts={'id_ipv4': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv4_letter(self):
        response = self.alter_vip(dicts={'id_ipv4': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv4_empty(self):
        response = self.alter_vip(dicts={'id_ipv4': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv4_none(self):
        response = self.alter_vip(dicts={'id_ipv4': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv4_zero(self):
        response = self.alter_vip(dicts={'id_ipv4': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid ipv6 id
    def test_vip_alter_ipv6_nonexistent(self):
        response = self.alter_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_vip_alter_ipv6_negative(self):
        response = self.alter_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv6_letter(self):
        response = self.alter_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv6_empty(self):
        response = self.alter_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv6_none(self):
        response = self.alter_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ipv6_zero(self):
        response = self.alter_vip(
            dicts={'id_ipv4': None, 'id_ipv6': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid id_healthcheck_expect
    def test_vip_alter_healthcheck_expect_nonexistent(self):
        response = self.alter_vip(
            dicts={'id_healthcheck_expect': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.HEALTHCHECKEXPECT_NOT_FOUND)

    def test_vip_alter_healthcheck_expect_negative(self):
        response = self.alter_vip(
            dicts={'id_healthcheck_expect': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_healthcheck_expect_letter(self):
        response = self.alter_vip(
            dicts={'id_healthcheck_expect': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_healthcheck_expect_empty(self):
        response = self.alter_vip(
            dicts={'id_healthcheck_expect': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_expect_none(self):
        response = self.alter_vip(
            dicts={'id_healthcheck_expect': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_expect_zero(self):
        response = self.alter_vip(
            dicts={'id_healthcheck_expect': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid vip environment
    def test_vip_alter_finality_nonexistent(self):
        response = self.alter_vip(dicts={'finalidade': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_alter_finality_none(self):
        response = self.alter_vip(dicts={'finalidade': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_finality_empty(self):
        response = self.alter_vip(dicts={'finalidade': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_finality_minsize(self):
        response = self.alter_vip(dicts={'finalidade': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_alter_finality_maxsize(self):
        response = self.alter_vip(dicts={'finalidade': string_generator(51)})
        self._attr_invalid(response)

    def test_vip_alter_client_nonexistent(self):
        response = self.alter_vip(dicts={'cliente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_alter_client_none(self):
        response = self.alter_vip(dicts={'cliente': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_client_empty(self):
        response = self.alter_vip(dicts={'cliente': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_client_minsize(self):
        response = self.alter_vip(dicts={'cliente': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_alter_client_maxsize(self):
        response = self.alter_vip(dicts={'cliente': string_generator(51)})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_nonexistent(self):
        response = self.alter_vip(dicts={'ambiente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_alter_p44_environment_none(self):
        response = self.alter_vip(dicts={'ambiente': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_empty(self):
        response = self.alter_vip(dicts={'ambiente': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_minsize(self):
        response = self.alter_vip(dicts={'ambiente': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_maxsize(self):
        response = self.alter_vip(dicts={'ambiente': string_generator(51)})
        self._attr_invalid(response)

    # Invalid cache
    def test_vip_alter_cache_nonexistent(self):
        response = self.alter_vip(dicts={'cache': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_minsize(self):
        response = self.alter_vip(dicts={'cache': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_maxsize(self):
        response = self.alter_vip(dicts={'cache': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_empty(self):
        response = self.alter_vip(dicts={'cache': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_none(self):
        response = self.alter_vip(dicts={'cache': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    # Invalid maxcon
    def test_vip_alter_maxcon_negative(self):
        response = self.alter_vip(dicts={'maxcon': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_maxcon_letter(self):
        response = self.alter_vip(dicts={'maxcon': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_maxcon_empty(self):
        response = self.alter_vip(dicts={'maxcon': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_maxcon_none(self):
        response = self.alter_vip(dicts={'maxcon': self.NONE_ATTR})
        self._attr_invalid(response)

    # Invalid balancing method
    def test_vip_alter_bal_method_nonexistent(self):
        response = self.alter_vip(dicts={'metodo_bal': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_minsize(self):
        response = self.alter_vip(dicts={'metodo_bal': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_maxsize(self):
        response = self.alter_vip(dicts={'metodo_bal': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_empty(self):
        response = self.alter_vip(dicts={'metodo_bal': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_none(self):
        response = self.alter_vip(dicts={'metodo_bal': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    # Invalid persistence
    def test_vip_alter_persistence_nonexistent(self):
        response = self.alter_vip(dicts={'persistencia': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_minsize(self):
        response = self.alter_vip(dicts={'persistencia': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_maxsize(self):
        response = self.alter_vip(dicts={'persistencia': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_empty(self):
        response = self.alter_vip(dicts={'persistencia': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_none(self):
        response = self.alter_vip(dicts={'persistencia': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    # Invalid healthcheck_type
    def test_vip_alter_healthcheck_type_nonexistent(self):
        response = self.alter_vip(
            dicts={'healthcheck_type': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_alter_healthcheck_type_empty(self):
        response = self.alter_vip(dicts={'healthcheck_type': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_alter_healthcheck_type_none(self):
        response = self.alter_vip(dicts={'healthcheck_type': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    # Invalid healthcheck URL
    def test_vip_alter_healthcheck_empty(self):
        response = self.alter_vip(dicts={'healthcheck': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_none(self):
        response = self.alter_vip(dicts={'healthcheck': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_invalid_tcp(self):
        response = self.alter_vip(
            dicts={'healthcheck_type': 'TCP', 'id_healthcheck_expect': self.NONE_ATTR, 'healthcheck': string_generator(10)})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_NOT_HTTP_NOT_NONE)

    # Invalid timeout
    def test_vip_alter_timeout_nonexistent(self):
        response = self.alter_vip(dicts={'timeout': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_minsize(self):
        response = self.alter_vip(dicts={'timeout': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_maxsize(self):
        response = self.alter_vip(dicts={'timeout': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_empty(self):
        response = self.alter_vip(dicts={'timeout': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_none(self):
        response = self.alter_vip(dicts={'timeout': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    # Invalid service ports
    def test_vip_alter_service_ports_invalid_first(self):
        response = self.alter_vip(
            dicts={'portas_servicos': {'porta': ['njk:8000']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_invalid_second(self):
        response = self.alter_vip(
            dicts={'portas_servicos': {'porta': ['80:---m']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_empty_first(self):
        response = self.alter_vip(
            dicts={'portas_servicos': {'porta': [':8000']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_empty_second(self):
        response = self.alter_vip(
            dicts={'portas_servicos': {'porta': ['80:']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_no_dict_entry(self):
        response = self.alter_vip(dicts={'portas_servicos': {}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_none(self):
        response = self.alter_vip(
            dicts={'portas_servicos': {'porta': self.NONE_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)

    def test_vip_alter_service_ports_empty(self):
        response = self.alter_vip(
            dicts={'portas_servicos': {'porta': self.EMPTY_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)

    # Invalid reals
    def test_vip_alter_reals_none(self):
        response = self.alter_vip(dicts={'reals': {'real': self.NONE_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_alter_reals_empty(self):
        response = self.alter_vip(dicts={'reals': {'real': self.EMPTY_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_alter_reals_invalid_equip(self):
        response = self.alter_vip(dicts={'reals': {
                                  'real': [{'real_name': string_generator(10), 'real_ip': '192.168.55.130'}]}})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_alter_reals_invalid_ip(self):
        response = self.alter_vip(dicts={'reals': {'real': [
                                  {'real_name': 'BalancingEquipForVip2', 'real_ip': string_generator(10)}]}})
        self._attr_invalid(response)

    def test_vip_alter_reals_no_equip(self):
        response = self.alter_vip(
            dicts={'reals': {'real': [{'real_ip': '192.168.55.130'}]}})
        self._attr_invalid(response)

    def test_vip_alter_reals_no_ip(self):
        response = self.alter_vip(
            dicts={'reals': {'real': [{'real_name': 'BalancingEquipForVip2'}]}})
        self._attr_invalid(response)

    # Invalid reals priorities
    def test_vip_alter_reals_priority_no_dict_entry(self):
        response = self.alter_vip(dicts={'reals_prioritys': {}})
        self._attr_invalid(response)

    def test_vip_alter_reals_priority_none(self):
        response = self.alter_vip(
            dicts={'reals_prioritys': {'reals_priority': self.NONE_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_alter_reals_priority_empty(self):
        response = self.alter_vip(
            dicts={'reals_prioritys': {'reals_priority': self.EMPTY_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    def test_vip_alter_reals_priority_letter(self):
        response = self.alter_vip(
            dicts={'reals_prioritys': {'reals_priority': [self.LETTER_ATTR]}})
        self._attr_invalid(response)

    def test_vip_alter_reals_priority_negative(self):
        response = self.alter_vip(
            dicts={'reals_prioritys': {'reals_priority': [self.NEGATIVE_ATTR]}})
        self._attr_invalid(response)

    def test_vip_alter_reals_priority_wrong_number(self):
        response = self.alter_vip(
            dicts={'reals_prioritys': {'reals_priority': [1, 2]}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_PRIORITY_WRONG_NUMBER_LIST)

    # Invalid reals weights
    def test_vip_alter_reals_weight_no_dict_entry(self):
        response = self.alter_vip(dicts={'reals_weights': {}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    def test_vip_alter_reals_weight_none(self):
        response = self.alter_vip(
            dicts={'reals_weights': {'reals_weight': self.NONE_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    def test_vip_alter_reals_weight_empty(self):
        response = self.alter_vip(
            dicts={'reals_weights': {'reals_weight': self.EMPTY_ATTR}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    def test_vip_alter_reals_weight_letter(self):
        response = self.alter_vip(
            dicts={'reals_weights': {'reals_weight': [self.LETTER_ATTR]}})
        self._attr_invalid(response)

    def test_vip_alter_reals_weight_negative(self):
        response = self.alter_vip(
            dicts={'reals_weights': {'reals_weight': [self.NEGATIVE_ATTR]}})
        self._attr_invalid(response)

    def test_vip_alter_reals_weight_wrong_number(self):
        response = self.alter_vip(
            dicts={'reals_weights': {'reals_weight': [1, 2]}})
        self._attr_invalid(
            response, CodeError.VIP_REALS_WEIGHT_WRONG_NUMBER_LIST)

    # RULE

    def test_vip_add_rule_invalid(self):
        response = self.alter_vip(dicts={'rule_id': 123})
        self._attr_invalid(response, CodeError.RULE_NOT_FIND)

    def test_vip_add_rule_letter(self):
        response = self.alter_vip(dicts={'rule_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_add_rule_negative(self):
        response = self.alter_vip(dicts={'rule_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_add_rule_zero(self):
        response = self.alter_vip(dicts={'rule_id': self.ZERO_ATTR})
        self._attr_invalid(response)


class VipRequestAlter2Test(VipRequestConfigTest, AttrTest):

    def test_vip_alter2_valid(self):
        response = self.alter2_vip()
        valid_response(response)

    def test_vip_alter_no_permission(self):
        response = self.alter2_vip(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_alter_no_write_permission(self):
        response = self.alter2_vip(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    # vip id
    def test_vip_alter_id_negative(self):
        response = self.alter2_vip(vip_id=self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_zero(self):
        response = self.alter2_vip(vip_id=self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_letter(self):
        response = self.alter2_vip(vip_id=self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_nonexistent(self):
        response = self.alter2_vip(vip_id=self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_alter_id_none(self):
        response = self.alter2_vip(vip_id=self.NONE_ATTR)
        self._attr_invalid(response)

    def test_vip_alter_id_empty(self):
        response = self.alter2_vip(vip_id=self.EMPTY_ATTR)
        self._attr_invalid(response)

    # Invalid ip id
    def test_vip_alter_ip_nonexistent(self):
        response = self.alter2_vip(dicts={'id_ip': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_FOUND)

    def test_vip_alter_ip_negative(self):
        response = self.alter2_vip(dicts={'id_ip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ip_letter(self):
        response = self.alter2_vip(dicts={'id_ip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ip_empty(self):
        response = self.alter2_vip(dicts={'id_ip': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ip_none(self):
        response = self.alter2_vip(dicts={'id_ip': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_ip_zero(self):
        response = self.alter2_vip(dicts={'id_ip': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid id_healthcheck_expect
    def test_vip_alter_healthcheck_expect_nonexistent(self):
        response = self.alter2_vip(
            dicts={'id_healthcheck_expect': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.HEALTHCHECKEXPECT_NOT_FOUND)

    def test_vip_alter_healthcheck_expect_negative(self):
        response = self.alter2_vip(
            dicts={'id_healthcheck_expect': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_healthcheck_expect_letter(self):
        response = self.alter2_vip(
            dicts={'id_healthcheck_expect': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_healthcheck_expect_empty(self):
        response = self.alter2_vip(
            dicts={'id_healthcheck_expect': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_expect_none(self):
        response = self.alter2_vip(
            dicts={'id_healthcheck_expect': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_expect_zero(self):
        response = self.alter2_vip(
            dicts={'id_healthcheck_expect': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Invalid vip environment
    def test_vip_alter_finality_nonexistent(self):
        response = self.alter2_vip(dicts={'finalidade': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_alter_finality_none(self):
        response = self.alter2_vip(dicts={'finalidade': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_finality_empty(self):
        response = self.alter2_vip(dicts={'finalidade': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_finality_minsize(self):
        response = self.alter2_vip(dicts={'finalidade': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_alter_finality_maxsize(self):
        response = self.alter2_vip(dicts={'finalidade': string_generator(51)})
        self._attr_invalid(response)

    def test_vip_alter_client_nonexistent(self):
        response = self.alter2_vip(dicts={'cliente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_alter_client_none(self):
        response = self.alter2_vip(dicts={'cliente': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_client_empty(self):
        response = self.alter2_vip(dicts={'cliente': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_client_minsize(self):
        response = self.alter2_vip(dicts={'cliente': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_alter_client_maxsize(self):
        response = self.alter2_vip(dicts={'cliente': string_generator(51)})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_nonexistent(self):
        response = self.alter2_vip(dicts={'ambiente': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD)

    def test_vip_alter_p44_environment_none(self):
        response = self.alter2_vip(dicts={'ambiente': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_empty(self):
        response = self.alter2_vip(dicts={'ambiente': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_minsize(self):
        response = self.alter2_vip(dicts={'ambiente': string_generator(2)})
        self._attr_invalid(response)

    def test_vip_alter_p44_environment_maxsize(self):
        response = self.alter2_vip(dicts={'ambiente': string_generator(51)})
        self._attr_invalid(response)

    # Invalid cache
    def test_vip_alter_cache_nonexistent(self):
        response = self.alter2_vip(dicts={'cache': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_minsize(self):
        response = self.alter2_vip(dicts={'cache': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_maxsize(self):
        response = self.alter2_vip(dicts={'cache': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_empty(self):
        response = self.alter2_vip(dicts={'cache': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    def test_vip_alter_cache_none(self):
        response = self.alter2_vip(dicts={'cache': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_CACHE_VALUE)

    # Invalid maxcon
    def test_vip_alter_maxcon_negative(self):
        response = self.alter2_vip(dicts={'maxcon': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_maxcon_letter(self):
        response = self.alter2_vip(dicts={'maxcon': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_maxcon_empty(self):
        response = self.alter2_vip(dicts={'maxcon': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_alter_maxcon_none(self):
        response = self.alter2_vip(dicts={'maxcon': self.NONE_ATTR})
        self._attr_invalid(response)

    # Invalid balancing method
    def test_vip_alter_bal_method_nonexistent(self):
        response = self.alter2_vip(dicts={'metodo_bal': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_minsize(self):
        response = self.alter2_vip(dicts={'metodo_bal': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_maxsize(self):
        response = self.alter2_vip(dicts={'metodo_bal': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_empty(self):
        response = self.alter2_vip(dicts={'metodo_bal': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    def test_vip_alter_bal_method_none(self):
        response = self.alter2_vip(dicts={'metodo_bal': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_BAL_METHOD_VALUE)

    # Invalid persistence
    def test_vip_alter_persistence_nonexistent(self):
        response = self.alter2_vip(
            dicts={'persistencia': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_minsize(self):
        response = self.alter2_vip(dicts={'persistencia': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_maxsize(self):
        response = self.alter2_vip(
            dicts={'persistencia': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_empty(self):
        response = self.alter2_vip(dicts={'persistencia': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    def test_vip_alter_persistence_none(self):
        response = self.alter2_vip(dicts={'persistencia': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PERSISTENCE_VALUE)

    # Invalid healthcheck_type
    def test_vip_alter_healthcheck_type_nonexistent(self):
        response = self.alter2_vip(
            dicts={'healthcheck_type': string_generator(10)})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_alter_healthcheck_type_empty(self):
        response = self.alter2_vip(dicts={'healthcheck_type': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    def test_vip_alter_healthcheck_type_none(self):
        response = self.alter2_vip(dicts={'healthcheck_type': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.VIP_INVALID_HEALTHCHECK_TYPE_VALUE)

    # Invalid healthcheck URL
    def test_vip_alter_healthcheck_empty(self):
        response = self.alter2_vip(dicts={'healthcheck': self.EMPTY_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_none(self):
        response = self.alter2_vip(dicts={'healthcheck': self.NONE_ATTR})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_HTTP_NOT_NONE)

    def test_vip_alter_healthcheck_invalid_tcp(self):
        response = self.alter2_vip(
            dicts={'healthcheck_type': 'TCP', 'id_healthcheck_expect': self.NONE_ATTR, 'healthcheck': string_generator(10)})
        self._attr_invalid(
            response, CodeError.HEALTHCHECK_EXPECT_NOT_HTTP_NOT_NONE)

    # Invalid timeout
    def test_vip_alter_timeout_nonexistent(self):
        response = self.alter2_vip(dicts={'timeout': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_minsize(self):
        response = self.alter2_vip(dicts={'timeout': string_generator(2)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_maxsize(self):
        response = self.alter2_vip(dicts={'timeout': string_generator(51)})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_empty(self):
        response = self.alter2_vip(dicts={'timeout': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    def test_vip_alter_timeout_none(self):
        response = self.alter2_vip(dicts={'timeout': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_TIMEOUT_VALUE)

    # Invalid service ports
    def test_vip_alter_service_ports_invalid_first(self):
        response = self.alter2_vip(
            dicts={'portas_servicos': {'porta': ['njk:8000']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_invalid_second(self):
        response = self.alter2_vip(
            dicts={'portas_servicos': {'porta': ['80:---m']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_empty_first(self):
        response = self.alter2_vip(
            dicts={'portas_servicos': {'porta': [':8000']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_empty_second(self):
        response = self.alter2_vip(
            dicts={'portas_servicos': {'porta': ['80:']}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_no_dict_entry(self):
        response = self.alter2_vip(dicts={'portas_servicos': {}})
        self._attr_invalid(response)

    def test_vip_alter_service_ports_none(self):
        response = self.alter2_vip(
            dicts={'portas_servicos': {'porta': self.NONE_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)

    def test_vip_alter_service_ports_empty(self):
        response = self.alter2_vip(
            dicts={'portas_servicos': {'porta': self.EMPTY_ATTR}})
        self._attr_invalid(response, CodeError.VIP_INVALID_SERVICE_PORTS_VALUE)


class VipRequestEnableRealsTest(VipRequestConfigTest, AttrTest):

    def test_vip_enable_real_valid(self):
        response = self.script_real(mock=self.mock_to_enable_real())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_enable_real_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_enable_real_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_enable_real_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_enable_real_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_enable_real_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_enable_real_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_enable_real_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_network_version_invalid(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_enable_real_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestDisableRealsTest(VipRequestConfigTest, AttrTest):

    def test_vip_disable_real_valid(self):
        response = self.script_real(mock=self.mock_to_disable_real())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_disable_real_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_disable_real_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_disable_real_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_disable_real_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_disable_real_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_disable_real_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_disable_real_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_network_version_invalid(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_disable_real_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestEnableRealsV6Test(VipRequestConfigTest, AttrTest):

    def test_vip_enable_real_v6_valid(self):
        response = self.script_real(mock=self.mock_to_enable_real_v6())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_enable_real_v6_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_enable_real_v6_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_enable_real_v6_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_enable_real_v6_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_enable_real_v6_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_enable_real_v6_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_network_version_invalid(self):
        response = self.script_real(mock=self.mock_to_enable_real_v6(), dicts={
                                    'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_enable_real_v6_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_enable_real_v6(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestDisableRealsV6Test(VipRequestConfigTest, AttrTest):

    def test_vip_disable_real_v6_valid(self):
        response = self.script_real(mock=self.mock_to_disable_real_v6())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_disable_real_v6_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_disable_real_v6_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_disable_real_v6_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_disable_real_v6_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_disable_real_v6_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_disable_real_v6_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_network_version_invalid(self):
        response = self.script_real(mock=self.mock_to_disable_real_v6(), dicts={
                                    'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_disable_real_v6_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_disable_real_v6(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestRemoveRealsTest(VipRequestConfigTest, AttrTest):

    def test_vip_remove_real_valid(self):
        response = self.script_real(mock=self.mock_to_remove_real())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_remove_real_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_remove_real_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_remove_real_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_remove_real_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_remove_real_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_remove_real_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_remove_real_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_network_version_invalid(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_remove_real_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestRemoveRealsV6Test(VipRequestConfigTest, AttrTest):

    def test_vip_remove_real_v6_valid(self):
        response = self.script_real(mock=self.mock_to_remove_real_v6())
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_vip_remove_real_v6_no_permission(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_remove_real_v6_no_read_permission(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_remove_real_v6_vip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'vip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_vip_remove_real_v6_vip_negative(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'vip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_vip_zero(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'vip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_vip_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'vip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_vip_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'vip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_vip_letter(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'vip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_ip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'ip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.IP_NOT_REGISTERED_FOR_EQUIP)

    def test_vip_remove_real_v6_ip_negative(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'ip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_ip_zero(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'ip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_ip_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'ip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_ip_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'ip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_ip_letter(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'ip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_equip_nonexistent(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'equip_id': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_vip_remove_real_v6_equip_negative(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'equip_id': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_equip_zero(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'equip_id': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_equip_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'equip_id': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_equip_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'equip_id': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_equip_letter(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'equip_id': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_operation_invalid(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'operation': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_operation_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'operation': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_operation_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'operation': self.NONE_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_network_version_invalid(self):
        response = self.script_real(mock=self.mock_to_remove_real_v6(), dicts={
                                    'network_version': string_generator(10)})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_network_version_empty(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'network_version': self.EMPTY_ATTR})
        self._attr_invalid(response)

    def test_vip_remove_real_v6_network_version_none(self):
        response = self.script_real(
            mock=self.mock_to_remove_real_v6(), dicts={'network_version': self.NONE_ATTR})
        self._attr_invalid(response)


class VipRequestValidateRealsTest(VipRequestConfigTest, AttrTest):

    def test_vip_validate_real_valid(self):
        mock = self.mock_to_valid_real()
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        return response

    def test_vip_validate_real_no_permission(self):
        mock = self.mock_to_valid_real()
        response = self.client_no_permission().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_validate_real_no_read_permission(self):
        mock = self.mock_to_valid_real()
        response = self.client_no_read_permission().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_vip_validate_real_valid_v6(self):
        mock = self.mock_to_valid_real_v6()
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        return response

    def test_vip_validate_real_nonexistent_4(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = '192.168.30.1'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response, CodeError.IP_NOT_RELATED_ENVIRONMENT_VIP)

    def test_vip_validate_real_invalid_chars_4(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = '192.168.20.1za'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_invalid_range_4(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = '192.168.20.1000'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_invalid_comma_4(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = '192,168,20,11'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_invalid_separators_4(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = '192.168/20;11'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_nonexistent_6(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = 'ffab:cdef:ffff:ffff:0000:0000:0000:0015'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response, CodeError.IP_NOT_RELATED_ENVIRONMENT_VIP)

    def test_vip_validate_real_invalid_chars_6(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = 'ffab:cdef:ffff:ffff:0000:0000:0000:0t1g'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_invalid_range_6(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = 'ffab:cdef:ffff:ffff:0000:0000:0000:150000'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_invalid_comma_6(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = 'ffab,cdef,ffff,ffff,0000,0000,0000,0011'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_invalid_separators_6(self):
        mock = self.mock_to_valid_real()
        mock['ip'] = 'ffab:cdef;ffff:ffff/0000:0000:0000:0015'
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_environment_nonexistent(self):
        mock = self.mock_to_valid_real()
        mock['id_environment_vip'] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_vip_validate_real_environment_negative(self):
        mock = self.mock_to_valid_real()
        mock['id_environment_vip'] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_environment_letter(self):
        mock = self.mock_to_valid_real()
        mock['id_environment_vip'] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_environment_zero(self):
        mock = self.mock_to_valid_real()
        mock['id_environment_vip'] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_environment_empty(self):
        mock = self.mock_to_valid_real()
        mock['id_environment_vip'] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_environment_none(self):
        mock = self.mock_to_valid_real()
        mock['id_environment_vip'] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_equipment_maxsize(self):
        mock = self.mock_to_valid_real()
        mock['name_equipment'] = string_generator(81)
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_equipment_minsize(self):
        mock = self.mock_to_valid_real()
        mock['name_equipment'] = string_generator(2)
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_equipment_empty(self):
        mock = self.mock_to_valid_real()
        mock['name_equipment'] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)

    def test_vip_validate_real_equipment_none(self):
        mock = self.mock_to_valid_real()
        mock['name_equipment'] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_VALIDATE_REAL, {'real': mock})
        self._attr_invalid(response)


class VipRequestAlterHealthcheckTest(VipRequestConfigTest, AttrTest):

    def test_alter_healthcheck_valid(self):
        response = self.alter_healthcheck()
        valid_response(response)

    def test_alter_healthcheck_no_permission(self):
        response = self.alter_healthcheck(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_healthcheck_no_write_permission(self):
        response = self.alter_healthcheck(
            client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    # vip id
    def test_alter_healthcheck_vip_id_negative(self):
        response = self.alter_healthcheck(vip_id=self.NEGATIVE_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_vip_id_zero(self):
        response = self.alter_healthcheck(vip_id=self.ZERO_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_vip_id_letter(self):
        response = self.alter_healthcheck(vip_id=self.LETTER_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_vip_id_nonexistent(self):
        response = self.alter_healthcheck(vip_id=self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_alter_healthcheck_vip_id_none(self):
        response = self.alter_healthcheck(vip_id=self.NONE_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_vip_id_empty(self):
        response = self.alter_healthcheck(vip_id=self.EMPTY_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    # healthcheck type
    def test_alter_healthcheck_healthcheck_type_invalid_str(self):
        response = self.alter_healthcheck(
            dicts={'healthcheck_type': string_generator(10)})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_healthcheck_type_number(self):
        response = self.alter_healthcheck(dicts={'healthcheck_type': 10})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_healthcheck_type_empty(self):
        response = self.alter_healthcheck(
            dicts={'healthcheck_type': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_healthcheck_type_none(self):
        response = self.alter_healthcheck(
            dicts={'healthcheck_type': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    # healthcheck
    def test_alter_healthcheck_healthcheck_empty(self):
        response = self.alter_healthcheck(
            dicts={'healthcheck': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_healthcheck_none(self):
        response = self.alter_healthcheck(
            dicts={'healthcheck': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    # id_healthcheck_expect
    def test_alter_healthcheck_id_healthcheck_expect_negative(self):
        response = self.alter_healthcheck(
            dicts={'id_healthcheck_expect': self.NEGATIVE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_id_healthcheck_expect_zero(self):
        response = self.alter_healthcheck(
            dicts={'id_healthcheck_expect': self.ZERO_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_id_healthcheck_expect_letter(self):
        response = self.alter_healthcheck(
            dicts={'id_healthcheck_expect': self.LETTER_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_id_healthcheck_expect_nonexistent(self):
        response = self.alter_healthcheck(
            dicts={'id_healthcheck_expect': self.ID_NONEXISTENT})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_id_healthcheck_expect_empty(self):
        response = self.alter_healthcheck(
            dicts={'id_healthcheck_expect': self.EMPTY_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_healthcheck_id_healthcheck_expect_none(self):
        response = self.alter_healthcheck(
            dicts={'id_healthcheck_expect': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)


class VipRequestAlterPriorityTest(VipRequestConfigTest, AttrTest):

    def test_alter_priority_valid(self):
        response = self.alter_priority()
        valid_response(response)

    def test_alter_priority_no_permission(self):
        response = self.alter_priority(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_priority_no_write_permission(self):
        response = self.alter_priority(client=CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    # vip id
    def test_alter_priority_vip_id_negative(self):
        response = self.alter_priority(vip_id=self.NEGATIVE_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_vip_id_zero(self):
        response = self.alter_priority(vip_id=self.ZERO_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_vip_id_letter(self):
        response = self.alter_priority(vip_id=self.LETTER_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_vip_id_nonexistent(self):
        response = self.alter_priority(vip_id=self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_alter_priority_vip_id_none(self):
        response = self.alter_priority(vip_id=self.NONE_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_vip_id_empty(self):
        response = self.alter_priority(vip_id=self.EMPTY_ATTR)
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    # priority
#    'reals_prioritys': {'reals_priority': [2]}
    def test_alter_priority_priority_letter(self):
        response = self.alter_priority(
            dicts={'reals_prioritys': {'reals_priority': [self.LETTER_ATTR]}})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_priority_negative(self):
        response = self.alter_priority(
            dicts={'reals_prioritys': {'reals_priority': [self.NEGATIVE_ATTR]}})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_priority_empty(self):
        response = self.alter_priority(
            dicts={'reals_prioritys': {'reals_priority': [self.EMPTY_ATTR]}})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_priority_none(self):
        response = self.alter_priority(
            dicts={'reals_prioritys': {'reals_priority': [self.NONE_ATTR]}})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_priority_wrong_number(self):
        response = self.alter_priority(
            dicts={'reals_prioritys': {'reals_priority': ['n', -2]}})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_priority_no_key(self):
        response = self.alter_priority(dicts={'reals_prioritys': {}})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_alter_priority_priority_none_dict(self):
        response = self.alter_priority(
            dicts={'reals_prioritys': self.NONE_ATTR})
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)


class VipRequestEditMaxconTest(VipRequestConfigTest, RemoveTest):

    def test_edit_valid(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.ID_VALID_VIP_EDIT_MAXCON, self.MAXCON_VALID))
        valid_response(response)

    def test_edit_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_EDIT_MAXCON % (self.ID_VALID_VIP_EDIT_MAXCON, self.MAXCON_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_edit_no_write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_EDIT_MAXCON % (self.ID_VALID_VIP_EDIT_MAXCON, self.MAXCON_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_edit_vip_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.ID_NONEXISTENT, self.MAXCON_VALID))
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

    def test_edit_vip_negative(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.NEGATIVE_ATTR, self.MAXCON_VALID))
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_edit_vip_letter(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.LETTER_ATTR, self.MAXCON_VALID))
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_edit_vip_zero(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.ZERO_ATTR, self.MAXCON_VALID))
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_edit_vip_empty(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.EMPTY_ATTR, self.MAXCON_VALID))
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_edit_maxcon_negative(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.ID_VALID_VIP_EDIT_MAXCON, self.NEGATIVE_ATTR))
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_edit_maxcon_letter(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.ID_VALID_VIP_EDIT_MAXCON, self.LETTER_ATTR))
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)

    def test_edit_maxcon_empty(self):
        response = self.client_autenticado().put(
            self.URL_EDIT_MAXCON % (self.ID_VALID_VIP_EDIT_MAXCON, self.EMPTY_ATTR))
        self._attr_invalid(response, CodeError.VIP_INVALID_PARAMETER)


class VipRequestConsultationSearchTest(VipRequestConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.VIP_REQUEST_NOT_FOUND
    URL_GET_BY_ID = VipRequestConfigTest.URL_SEARCH

    def test_search_valid(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_no_permission(self):
        response = self.get_by_id(self.ID_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_search_no_read_permission(self):
        response = self.get_by_id(
            self.ID_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_search_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_search_negative(self):
        self.get_by_id_negative()

    def test_search_letter(self):
        self.get_by_id_letter()

    def test_search_zero(self):
        self.get_by_id_zero()

    def test_search_empty(self):
        self.get_by_id_empty()

    def test_search_paginate_no_permission(self):
        response = self.search_paginate(client=CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_search_paginate_no_read_permission(self):
        response = self.search_paginate(client=CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_search_paginate_valid(self):
        response = self.search_paginate()
        valid_response(response)
        content = valid_content(response, 'vips')
        total = valid_content(response, 'total')
        assert int(total) > 0 and len(content) <= int(total)

    def test_search_paginate_id_vip_valid(self):
        response = self.search_paginate(dicts={'id_vip': self.ID_VALID})
        valid_response(response)
        total = valid_content(response, 'total')
        content = valid_content(response, 'vips')
        if type(content) == dict:
            content = [content]
        assert int(total) == 1 and len(content) == int(total)

    def test_search_paginate_id_vip_nonexistent(self):
        response = self.search_paginate(dicts={'id_vip': self.ID_NONEXISTENT})
        valid_response(response)
        total = valid_content(response, 'total')
        assert int(total) == 0

    def test_search_paginate_id_vip_letter(self):
        response = self.search_paginate(dicts={'id_vip': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_paginate_id_vip_negative(self):
        response = self.search_paginate(dicts={'id_vip': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_paginate_id_vip_zero(self):
        response = self.search_paginate(dicts={'id_vip': self.ZERO_ATTR})
        self._attr_invalid(response)

    def test_search_paginate_ipv4_valid(self):
        response = self.search_paginate(dicts={'ip': '192.168.55.122'})
        valid_response(response)
        total = valid_content(response, 'total')
        content = valid_content(response, 'vips')
        if type(content) == dict:
            content = [content]
        assert int(total) == 1 and len(content) == int(total)

    def test_search_paginate_ipv4_nonexistent(self):
        response = self.search_paginate(dicts={'ip': '192.168.55.222'})
        valid_response(response)
        total = valid_content(response, 'total')
        assert int(total) == 0

    def test_search_paginate_ipv4_invalid_chars(self):
        response = self.search_paginate(dicts={'ip': '192.168.55.1za'})
        self._attr_invalid(response)

    def test_search_paginate_ipv4_invalid_range(self):
        response = self.search_paginate(dicts={'ip': '192.168.55.1000'})
        self._attr_invalid(response)

    def test_search_paginate_ipv4_invalid_comma(self):
        response = self.search_paginate(dicts={'ip': '192,168,55,122'})
        self._attr_invalid(response)

    def test_search_paginate_ipv4_invalid_separators(self):
        response = self.search_paginate(dicts={'ip': '192.168/55;122'})
        self._attr_invalid(response)

    def test_search_paginate_ipv6_valid(self):
        response = self.search_paginate(
            dicts={'ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:0122'})
        valid_response(response)
        total = valid_content(response, 'total')
        content = valid_content(response, 'vips')
        if type(content) == dict:
            content = [content]
        assert int(total) == 1 and len(content) == int(total)

    def test_search_paginate_ipv6_nonexistent(self):
        response = self.search_paginate(
            dicts={'ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:2122'})
        valid_response(response)
        total = valid_content(response, 'total')
        assert int(total) == 0

    def test_search_paginate_ipv6_invalid_chars(self):
        response = self.search_paginate(
            dicts={'ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:uugd'})
        self._attr_invalid(response)

    def test_search_paginate_ipv6_invalid_range(self):
        response = self.search_paginate(
            dicts={'ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:90122'})
        self._attr_invalid(response)

    def test_search_paginate_ipv6_invalid_comma(self):
        response = self.search_paginate(
            dicts={'ip': 'ffab,cdef,ffff,ffff,0000,0000,0000,0122'})
        self._attr_invalid(response)

    def test_search_paginate_ipv6_invalid_separators(self):
        response = self.search_paginate(
            dicts={'ip': 'ffab:cdef/ffff.ffff;0000.0000.0000:0122'})
        self._attr_invalid(response)

    def test_search_paginate_create_valid_true(self):
        response = self.search_paginate(dicts={'create': 'True'})
        valid_response(response)
        total = valid_content(response, 'total')
        content = valid_content(response, 'vips')
        if type(content) == dict:
            content = [content]
        assert int(total) > 0 and len(content) == int(total)

    def test_search_paginate_create_valid_false(self):
        response = self.search_paginate(dicts={'create': 'False'})
        valid_response(response)
        total = valid_content(response, 'total')
        content = valid_content(response, 'vips')
        if type(content) == dict:
            content = [content]
        assert int(total) > 0 and len(content) <= int(total)

    def test_search_paginate_create_invalid(self):
        response = self.search_paginate(dicts={'create': string_generator(10)})
        self._attr_invalid(response)


class VipRequestAddBlock(VipRequestConfigTest, AttrTest):
    NONEXISTENT = 34582
    ID_VIP_TO_ADD_BLOCK = 36
    ID_VIP_TO_ADD_BLOCK_NO_BLOCKS_IN_FILTER = 37
    ID_VIP_TO_WITHOUT_BLOCK_IN_ENVIRONMENT = 1
    ID_BLOCK_ALREADY_IN_RULE = 2
    ID_BLOCK = 3
    OVERRIDE = 1

    def test_add_block_valid(self):
        response = self.client_autenticado().get(
            self.URL_ADD_BLOCK % (self.ID_VIP_TO_ADD_BLOCK, self.ID_BLOCK, self.OVERRIDE))
        valid_response(response)

    def test_add_block_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_ADD_BLOCK % (self.NONEXISTENT, self.ID_BLOCK, self.OVERRIDE))
        self._attr_invalid(response, CodeError.VIP_REQUEST_NOT_FOUND)

        response = self.client_autenticado().get(
            self.URL_ADD_BLOCK % (self.ID_VIP_TO_ADD_BLOCK, self.NONEXISTENT, self.OVERRIDE))
        self._attr_invalid(response, CodeError.BLOCK_NOT_FOUND)

    def test_add_block_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_ADD_BLOCK % (self.ID_VIP_TO_ADD_BLOCK, self.ID_BLOCK, self.OVERRIDE))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_add_block_no_write_permission(self):
        response = self.client_no_write_permission().get(
            self.URL_ADD_BLOCK % (self.ID_VIP_TO_ADD_BLOCK, self.ID_BLOCK, self.OVERRIDE))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_add_block_no_block_associated(self):
        # No block for environment
        response = self.client_autenticado().get(self.URL_ADD_BLOCK % (
            self.ID_VIP_TO_WITHOUT_BLOCK_IN_ENVIRONMENT, self.ID_BLOCK, self.OVERRIDE))
        self._attr_invalid(response, CodeError.BLOCK_NOT_FOUND)

    def test_add_block_already_in_rule(self):
        response = self.client_autenticado().get(self.URL_ADD_BLOCK % (
            self.ID_VIP_TO_ADD_BLOCK, self.ID_BLOCK_ALREADY_IN_RULE, self.OVERRIDE))
        self._attr_invalid(response, CodeError.VIPREQUESTBLOCKALREADYINRULE)

    def test_add_block_no_blocks_in_filter(self):
        response = self.client_autenticado().get(self.URL_ADD_BLOCK % (
            self.ID_VIP_TO_ADD_BLOCK_NO_BLOCKS_IN_FILTER, self.ID_BLOCK, self.OVERRIDE))
        self._attr_invalid(response, CodeError.VIPREQUESTNOBLOCKINRULE)
