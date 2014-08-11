# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.db.models import Q
from django.forms.models import model_to_dict
from networkapi.vlan.models import Vlan
from networkapi.test import BasicTestCase, me, CodeError, ConsultationTest, me, AttrTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, valid_get_all, valid_get_filtered, string_generator
import httplib


class VlanConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/vlan/fixtures/initial_data.yaml']
    XML_KEY = "vlan"
    ID_VALID = 1
    ID_ALTER_VALID = 2
    ID_REMOVE_VALID = 3
    ID_REMOVE_SCRIPT_VALID = 6
    ID_VALID_WITH_NET = 7
    ID_VLAN_WITHOUT_NET = 4
    ID_REMOVE_SCRIPT_ACTIVE = 13
    OBJ = Vlan

    ID_ENVIRONMENT_VALID = 1
    ID_ENV_VALID_TO_ALLOCATE = 10
    ID_ENV_VALID_TO_ALLOCATE_V6 = 11
    ID_ENV_VALID_TO_ALLOCATE_NO_NET = 12
    ID_VLAN_FOR_VALIDATE = 4
    ID_VLAN_FOR_INVALIDATE = 5

    ID_NETV4_CREATE_SCRIPT = 16
    ID_NETV6_CREATE_SCRIPT = 15

    # Urls
    URL_GET_ALL = "/vlan/all/"
    URL_GET_BY_ENVIRONMENT = "/vlan/ambiente/%s/"
    URL_GET_BY_ID_WITH_NETWORKS = "/vlan/%s/network/"
    URL_SEARCH = "/vlan/find/"
    URL_SAVE = "/vlan/insert/"
    URL_ALTER = "/vlan/edit/"
    URL_DEALLOCATE = "/vlan/%s/deallocate/"
    URL_VALIDATE_ACL_v4 = "/vlan/%s/validate/v4/"
    URL_VALIDATE_ACL_v6 = "/vlan/%s/validate/v6/"
    URL_INVALIDATE_ACL_v4 = "/vlan/%s/invalidate/v4/"
    URL_INVALIDATE_ACL_v6 = "/vlan/%s/invalidate/v6/"
    URL_REMOVE_SCRIPT = "/vlan/%s/remove/"
    URL_LIST_PERMISSION = "/vlan/list/"
    URL_CHECK_PERMISSION = "/vlan/%s/check/"
    URL_ADD_PERMISSION = "/vlan/%s/add/"
    URL_REMOVE_PERMISSION = "/vlan/%s/del/"
    URL_GET_BY_ID = "/vlan/%s/"
    URL_ALLOCATE_VLAN = "/vlan/"
    URL_ALLOCATE_VLAN_V6 = "/vlan/ipv6/"
    URL_ALLOCATE_NO_NETWORK = "/vlan/no-network/"
    URL_CREATE_SCRIPT = "/vlan/%s/criar/"
    URL_CREATE_SCRIPT_NET4 = "/vlan/v4/create/"
    URL_CREATE_SCRIPT_NET6 = "/vlan/v6/create/"
    URL_CHECK_NUMBER = "/vlan/check_number_available/%s/%s/%s/"

    def mock_valid_id_1(self):
        mock = {}
        mock["nome"] = "VLANVALIDA"
        mock["num_vlan"] = 1
        mock["ambiente"] = 1
        mock["descricao"] = "Descricao da vlan valida"
        mock["acl_file_name"] = "ACLVLANVALIDA"
        mock["acl_valida"] = False
        mock["acl_file_name_v6"] = "ACLVLANVALIDAV6"
        mock["acl_valida_v6"] = False
        mock["ativada"] = False
        return mock

    def mock_valid(self):
        mock = {}
        mock["name"] = "MOCK"
        mock["number"] = 10
        mock["environment_id"] = 1
        mock["description"] = "mock"
        mock["acl_file"] = "ACLMOCK"
        mock["acl_file_v6"] = "ACLMOCKV6"
        mock["network_ipv4"] = "0"
        mock["network_ipv6"] = "0"
        return mock

    def mock_valid_alter(self):
        mock = {}
        mock["vlan_id"] = self.ID_ALTER_VALID
        mock["name"] = "VLANCHANGED"
        mock["number"] = 20
        mock["environment_id"] = 1
        mock["description"] = "mock"
        mock["acl_file"] = "ACLMOCKALTER"
        mock["acl_file_v6"] = "ACLMOCKV6ALTER"
        return mock

    def mock_valid_allocate(self):
        mock = {}
        mock['nome'] = 'VLANALLOCATE'
        mock['id_tipo_rede'] = 1
        mock['id_ambiente'] = self.ID_ENV_VALID_TO_ALLOCATE
        mock['descricao'] = 'Vlan allocate description'
        mock['id_ambiente_vip'] = 1
        return mock

    def mock_valid_allocate_v6(self):
        mock = {}
        mock['name'] = 'VLANALLOCATEV6'
        mock['id_network_type'] = 1
        mock['id_environment'] = self.ID_ENV_VALID_TO_ALLOCATE_V6
        mock['description'] = 'Vlan allocate description v6'
        mock['id_environment_vip'] = 1
        return mock

    def mock_valid_allocate_no_net(self):
        mock = {}
        mock['environment_id'] = self.ID_ENV_VALID_TO_ALLOCATE_NO_NET
        mock['name'] = 'VLANALLOCATENONETWORK'
        mock['description'] = 'Vlan allocate description no net'
        return mock

    def mock_to_search(self):
        mock = {}
        mock["start_record"] = 0
        mock["end_record"] = 25
        mock["asorting_cols"] = []
        mock["searchable_columns"] = []
        mock["custom_search"] = ''

        mock["numero"] = None
        mock["nome"] = None
        mock["exato"] = False
        mock["ambiente"] = None
        mock["tipo_rede"] = None
        mock["rede"] = None
        mock["versao"] = 2
        mock["subrede"] = None
        mock["acl"] = None
        return mock

    def mock_list_permission(self):
        mock = {}
        mock["nome"] = "EquipmentForInterface"
        mock["nome_interface"] = "InterfaceForVlanLP"
        return mock

    def valid_attr(self, mock, obj):
        assert str(mock["nome"]) == str(obj["nome"])
        assert str(mock["num_vlan"]) == str(obj["num_vlan"])
        assert str(mock["ambiente"]) == str(obj["ambiente"])
        assert str(mock["descricao"]) == str(obj["descricao"])
        assert str(mock["acl_file_name"]) == str(obj["acl_file_name"])
        assert str(mock["acl_valida"]) == str(obj["acl_valida"])
        assert str(mock["acl_file_name_v6"]) == str(obj["acl_file_name_v6"])
        assert str(mock["acl_valida_v6"]) == str(obj["acl_valida_v6"])
        assert str(mock["ativada"]) == str(obj["ativada"])

    def valid_attr_save_alter(self, mock, obj):
        assert str(mock["name"]) == str(obj["nome"])
        assert str(mock["number"]) == str(obj["num_vlan"])
        assert str(mock["environment_id"]) == str(obj["ambiente"])
        assert str(mock["description"]) == str(obj["descricao"])
        assert str(mock["acl_file"]) == str(obj["acl_file_name"])
        assert str(mock["acl_file_v6"]) == str(obj["acl_file_name_v6"])

    def alter_attr_invalid(self, attr, code_error=None):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = attr
        response = self.client_autenticado().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        self._attr_invalid(response, code_error)

    def search_attr(self, dicts):
        mock = self.mock_to_search()
        for (k, v) in dicts.iteritems():
            mock[k] = v
        response = self.client_autenticado().postXML(
            self.URL_SEARCH, {self.XML_KEY: mock})
        return response

    def permission_script(self, url, key=None, attr=None):
        mock = self.mock_list_permission()
        if key is not None:
            mock[key] = attr
        response = self.client_autenticado().putXML(url, {'equipamento': mock})
        return response

    def allocate_invalid(self, key, attr):
        mock = self.mock_valid_allocate()
        mock[key] = attr
        response = self.client_autenticado().postXML(
            self.URL_ALLOCATE_VLAN, {self.XML_KEY: mock})
        return response

    def allocate_invalid_v6(self, key, attr):
        mock = self.mock_valid_allocate_v6()
        mock[key] = attr
        response = self.client_autenticado().postXML(
            self.URL_ALLOCATE_VLAN_V6, {self.XML_KEY: mock})
        return response

    def allocate_invalid_no_net(self, key, attr):
        mock = self.mock_valid_allocate_no_net()
        mock[key] = attr
        response = self.client_autenticado().postXML(
            self.URL_ALLOCATE_NO_NETWORK, {self.XML_KEY: mock})
        return response


class VlanConsultationTest(VlanConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND
    CODE_ERROR_ENVIRONMENT_NOT_FOUND = CodeError.ENVIRONMENT_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        valid_get_all(content, self.OBJ)

    def test_get_all_inactive(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response, httplib.UNAUTHORIZED)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_with_network_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID_WITH_NETWORKS % self.ID_VALID)
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        mock = self.mock_valid_id_1()
        self.valid_attr(mock, content)

    def test_get_by_id_with_network_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID_WITH_NETWORKS % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_id_with_network_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID_WITH_NETWORKS % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_id_with_network_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID_WITH_NETWORKS % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_id_with_network_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID_WITH_NETWORKS % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_id_with_network_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID_WITH_NETWORKS % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % self.ID_ENVIRONMENT_VALID)
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        query = Q(ambiente=self.ID_ENVIRONMENT_VALID)
        valid_get_filtered(content, self.OBJ, query)

    def test_get_by_environment_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % self.ID_NONEXISTENT)
        self._not_found(response, self.CODE_ERROR_ENVIRONMENT_NOT_FOUND)

    def test_get_by_environment_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % self.EMPTY_ATTR)
        self._attr_invalid(response)


class VlanTest(VlanConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, self.XML_KEY)

        vlan = Vlan().get_by_pk(content["id"])
        self.valid_attr_save_alter(mock, model_to_dict(vlan))

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_valid_alter()
        response = self.client_autenticado().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response)

        vlan = Vlan().get_by_pk(self.ID_ALTER_VALID)
        self.valid_attr_save_alter(mock, model_to_dict(vlan))

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.client_no_permission().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class VlanValidateTest(VlanConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def test_validate_v4_valid(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v4 % self.ID_VLAN_FOR_VALIDATE)
        valid_response(response)

    def test_validate_v4_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_VALIDATE_ACL_v4 % self.ID_VLAN_FOR_VALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_validate_v4_no_write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_VALIDATE_ACL_v4 % self.ID_VLAN_FOR_VALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_validate_v4_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v4 % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_validate_v4_negative(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v4 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_validate_v4_letter(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v4 % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_validate_v4_zero(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v4 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_validate_v4_empty(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v4 % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_validate_v6_valid(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v6 % self.ID_VLAN_FOR_VALIDATE)
        valid_response(response)

    def test_validate_v6_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_VALIDATE_ACL_v6 % self.ID_VLAN_FOR_VALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_validate_v6_no_write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_VALIDATE_ACL_v6 % self.ID_VLAN_FOR_VALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_validate_v6_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v6 % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_validate_v6_negative(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v6 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_validate_v6_letter(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v6 % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_validate_v6_zero(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v6 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_validate_v6_empty(self):
        response = self.client_autenticado().put(
            self.URL_VALIDATE_ACL_v6 % self.EMPTY_ATTR)
        self._attr_invalid(response)


class VlanInvalidateTest(VlanConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def test_invalidate_v4_valid(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v4 % self.ID_VLAN_FOR_INVALIDATE)
        valid_response(response)

    def test_invalidate_v4_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_INVALIDATE_ACL_v4 % self.ID_VLAN_FOR_INVALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_invalidate_v4_no_write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_INVALIDATE_ACL_v4 % self.ID_VLAN_FOR_INVALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_invalidate_v4_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v4 % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_invalidate_v4_negative(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v4 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_invalidate_v4_letter(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v4 % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_invalidate_v4_zero(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v4 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_invalidate_v4_empty(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v4 % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_invalidate_v6_valid(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v6 % self.ID_VLAN_FOR_INVALIDATE)
        valid_response(response)

    def test_invalidate_v6_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_INVALIDATE_ACL_v6 % self.ID_VLAN_FOR_INVALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_invalidate_v6_no_write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_INVALIDATE_ACL_v6 % self.ID_VLAN_FOR_INVALIDATE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_invalidate_v6_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v6 % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_invalidate_v6_negative(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v6 % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_invalidate_v6_letter(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v6 % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_invalidate_v6_zero(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v6 % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_invalidate_v6_empty(self):
        response = self.client_autenticado().put(
            self.URL_INVALIDATE_ACL_v6 % self.EMPTY_ATTR)
        self._attr_invalid(response)


class VlanAttrNameTest(VlanConfigTest, AttrTest):

    KEY_ATTR = "name"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        vlan = model_to_dict(Vlan().get_by_pk(self.ID_VALID))

        mock = self.mock_valid()
        mock[self.KEY_ATTR] = vlan['nome']
        self.process_save_attr_invalid(mock, CodeError.VLAN_DUPLICATE)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        self.alter_attr_invalid(string_generator(51))

    def test_alter_minsize(self):
        self.alter_attr_invalid(string_generator(2))

    def test_alter_unique(self):
        vlan = model_to_dict(Vlan().get_by_pk(self.ID_VALID))
        self.alter_attr_invalid(vlan['nome'], CodeError.VLAN_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_invalid(self.EMPTY_ATTR)

    def test_alter_none(self):
        self.alter_attr_invalid(self.NONE_ATTR)


class VlanAttrNumVlanTest(VlanConfigTest, AttrTest):

    KEY_ATTR = "number"

    def test_save_duplicated(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 1
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response, CodeError.VLAN_NUMBER_DUPLICATE)

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

    def test_alter_duplicated(self):
        self.alter_attr_invalid(1, CodeError.VLAN_NUMBER_DUPLICATE)

    def test_alter_negative(self):
        self.alter_attr_invalid(self.NEGATIVE_ATTR)

    def test_alter_letter(self):
        self.alter_attr_invalid(self.LETTER_ATTR)

    def test_alter_zero(self):
        self.alter_attr_invalid(self.ZERO_ATTR)

    def test_alter_empty(self):
        self.alter_attr_invalid(self.EMPTY_ATTR)

    def test_alter_none(self):
        self.alter_attr_invalid(self.NONE_ATTR)


class VlanAttrNumberCheckTest(VlanConfigTest, ConsultationTest):
    KEY_ATTR = "number"
    NUM_VLAN_IN_ENV_1 = 1
    NUM_VLAN_VALID = 10
    NUM_VLAN_INVALID = 10000000
    IS_INSERT = 'False'

    def test_check_valid_number(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER % (
            self.ID_ENV_VALID_TO_ALLOCATE_V6, self.NUM_VLAN_VALID, self.IS_INSERT))
        valid_response(response)
        content = valid_content(response, 'has_numbers_availables')
        assert content == 'True'

    def test_check_number_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_DEALLOCATE % self.ID_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_check_invalid_number(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER % (
            self.ID_ENV_VALID_TO_ALLOCATE_V6, self.NUM_VLAN_INVALID, self.IS_INSERT))
        valid_response(response)
        content = valid_content(response, 'has_numbers_availables')
        assert content == 'False'

    def test_check_valid_number_existent(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.ID_ENVIRONMENT_VALID, self.NUM_VLAN_IN_ENV_1, self.IS_INSERT))
        valid_response(response)
        content = valid_content(response, 'has_numbers_availables')
        # Returned true, this means that dont need confirmation, the system
        # will return exception when try to insert vlan
        assert content == 'True'

    def test_check_number_env_nonexistent(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.ID_NONEXISTENT, self.NUM_VLAN_VALID, self.IS_INSERT))
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_check_number_env_negative(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.NEGATIVE_ATTR, self.NUM_VLAN_VALID, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_env_letter(self):
        response = self.client_autenticado().get(
            self.URL_CHECK_NUMBER % (self.LETTER_ATTR, self.NUM_VLAN_VALID, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_env_zero(self):
        response = self.client_autenticado().get(
            self.URL_CHECK_NUMBER % (self.ZERO_ATTR, self.NUM_VLAN_VALID, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_env_empty(self):
        response = self.client_autenticado().get(
            self.URL_CHECK_NUMBER % (self.EMPTY_ATTR, self.NUM_VLAN_VALID, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_env_none(self):
        response = self.client_autenticado().get(
            self.URL_CHECK_NUMBER % (self.NONE_ATTR, self.NUM_VLAN_VALID, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_negative(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.ID_ENVIRONMENT_VALID, self.NEGATIVE_ATTR, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_letter(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.ID_ENVIRONMENT_VALID, self.LETTER_ATTR, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_zero(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.ID_ENVIRONMENT_VALID, self.ZERO_ATTR, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_empty(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.ID_ENVIRONMENT_VALID, self.EMPTY_ATTR, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_none(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER %
                                                 (self.ID_ENVIRONMENT_VALID, self.NONE_ATTR, self.IS_INSERT))
        self._attr_invalid(response)

    def test_check_number_id_vlan_nonexistent(self):
        response = self.client_autenticado().get(self.URL_CHECK_NUMBER % (
            self.ID_ENVIRONMENT_VALID, self.NUM_VLAN_VALID, self.ID_NONEXISTENT))
        self._attr_invalid(response, CodeError.VLAN_NOT_FOUND)


class VlanAttrAmbienteTest(VlanConfigTest, AttrTest):

    KEY_ATTR = "environment_id"

    def test_save_nonexistent(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

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
        self.alter_attr_invalid(
            self.ID_NONEXISTENT, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_alter_negative(self):
        self.alter_attr_invalid(self.NEGATIVE_ATTR)

    def test_alter_letter(self):
        self.alter_attr_invalid(self.LETTER_ATTR)

    def test_alter_zero(self):
        self.alter_attr_invalid(self.ZERO_ATTR)

    def test_alter_empty(self):
        self.alter_attr_invalid(self.EMPTY_ATTR)

    def test_alter_none(self):
        self.alter_attr_invalid(self.NONE_ATTR)


class VlanAttrDescricaoTest(VlanConfigTest, AttrTest):

    KEY_ATTR = "description"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_alter_maxsize(self):
        self.alter_attr_invalid(string_generator(201))

    def test_alter_minsize(self):
        self.alter_attr_invalid(string_generator(2))


class VlanAttrAclFileNameTest(VlanConfigTest, AttrTest):

    KEY_ATTR = "acl_file"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_duplicated(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'ACLVLANVALIDA'
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response, CodeError.VLAN_ACL_DUPLICATE)

    def test_alter_maxsize(self):
        self.alter_attr_invalid(string_generator(201))

    def test_alter_minsize(self):
        self.alter_attr_invalid(string_generator(2))

    def test_alter_duplicated(self):
        self.alter_attr_invalid('ACLVLANVALIDA', CodeError.VLAN_ACL_DUPLICATE)


class VlanAttrAclFileNamev6Test(VlanConfigTest, AttrTest):

    KEY_ATTR = "acl_file_v6"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_duplicated(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'ACLVLANVALIDAV6'
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response, CodeError.VLAN_ACL_DUPLICATE)

    def test_alter_maxsize(self):
        self.alter_attr_invalid(string_generator(201))

    def test_alter_minsize(self):
        self.alter_attr_invalid(string_generator(2))

    def test_alter_duplicated(self):
        self.alter_attr_invalid(
            'ACLVLANVALIDAV6', CodeError.VLAN_ACL_DUPLICATE)


class VlanDeallocateTest(VlanConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def test_deallocate_valid(self):
        response = self.client_autenticado().delete(
            self.URL_DEALLOCATE % self.ID_REMOVE_VALID)
        valid_response(response)

    def test_deallocate_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_DEALLOCATE % self.ID_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_deallocate_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_DEALLOCATE % self.ID_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_deallocate_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_DEALLOCATE % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_deallocate_negative(self):
        response = self.client_autenticado().delete(
            self.URL_DEALLOCATE % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_deallocate_letter(self):
        response = self.client_autenticado().delete(
            self.URL_DEALLOCATE % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_deallocate_zero(self):
        response = self.client_autenticado().delete(
            self.URL_DEALLOCATE % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_deallocate_empty(self):
        response = self.client_autenticado().delete(
            self.URL_DEALLOCATE % self.EMPTY_ATTR)
        self._attr_invalid(response)


class VlanSearchTest(VlanConfigTest):

    def test_search_valid(self):
        mock = self.mock_to_search()
        response = self.client_autenticado().postXML(
            self.URL_SEARCH, {self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_no_permission(self):
        mock = self.mock_to_search()
        response = self.client_no_permission().postXML(
            self.URL_SEARCH, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_search_no_read_permission(self):
        mock = self.mock_to_search()
        response = self.client_no_read_permission().postXML(
            self.URL_SEARCH, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class VlanSearchAttrsTest(VlanConfigTest, AttrTest):

    # Attribute number

    def test_search_number_valid(self):
        response = self.search_attr({'numero': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_number_letter(self):
        response = self.search_attr({'numero': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_number_negative(self):
        response = self.search_attr({'numero': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_number_zero(self):
        response = self.search_attr({'numero': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Attribute nome
    def test_search_name_valid(self):
        response = self.search_attr({'nome': 'VLANVALIDA'})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_name_minsize(self):
        response = self.search_attr({'nome': string_generator(2)})
        self._attr_invalid(response)

    # Attribute exato
    def test_search_exact_valid(self):
        response = self.search_attr({'nome': 'VLANVALIDA', 'exato': '1'})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_exact_invalid(self):
        response = self.search_attr(
            {'nome': 'VLANVALIDA', 'exato': string_generator(4)})
        self._attr_invalid(response)

    # Attribute ambiente
    def test_search_env_valid(self):
        response = self.search_attr({'ambiente': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_env_letter(self):
        response = self.search_attr({'ambiente': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_env_negative(self):
        response = self.search_attr({'ambiente': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_env_zero(self):
        response = self.search_attr({'ambiente': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Attribute tipo_rede
    def test_search_nettype_valid(self):
        response = self.search_attr({'tipo_rede': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_nettype_letter(self):
        response = self.search_attr({'tipo_rede': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_nettype_negative(self):
        response = self.search_attr({'tipo_rede': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_nettype_zero(self):
        response = self.search_attr({'tipo_rede': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Attribute acl
    def test_search_acl_valid(self):
        response = self.search_attr({'acl': '1'})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_acl_invalid(self):
        response = self.search_attr({'acl': string_generator(4)})
        self._attr_invalid(response)

    # Attribute versao
    def test_search_version_valid(self):
        response = self.search_attr({'versao': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_version_letter(self):
        response = self.search_attr({'versao': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_version_negative(self):
        response = self.search_attr({'versao': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    # Attribute rede e subrede
    def test_search_net_subnet_valid(self):
        response = self.search_attr(
            {'rede': '192.168.20.0/24', 'subrede': self.ZERO_ATTR})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_net_subnet_valid_v6(self):
        response = self.search_attr(
            {'rede': 'ffab:cdef:ffff:ffff:0000:0000:0000:0000/112', 'subrede': self.ZERO_ATTR})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_search_net_subnet_invalid(self):
        response = self.search_attr({'rede': '192.168.20.0/24', 'subrede': 2})
        self._attr_invalid(response)

    def test_search_net_subnet_negative(self):
        response = self.search_attr(
            {'rede': '192.168.20.0/24', 'subrede': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_net_subnet_letter(self):
        response = self.search_attr(
            {'rede': '192.168.20.0/24', 'subrede': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_net_invalid_subnet(self):
        response = self.search_attr(
            {'rede': '192.168.20.300/24', 'subrede': 0})
        self._attr_invalid(response)

    def test_search_net_letter_subnet(self):
        response = self.search_attr({'rede': '192.1ay.20.0/24', 'subrede': 0})
        self._attr_invalid(response)

    def test_composed_name_number_valid(self):
        response = self.search_attr({'numero': 1, 'nome': 'VLANVALIDA'})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_composed_name_number_letter(self):
        response = self.search_attr(
            {'numero': self.LETTER_ATTR, 'nome': 'VLANVALIDA'})
        self._attr_invalid(response)

    def test_composed_name_minsize_number(self):
        response = self.search_attr({'numero': 1, 'nome': string_generator(2)})
        self._attr_invalid(response)


class VlanRemoveScriptTest(VlanConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def teste_remove_script_valid_active(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.ID_REMOVE_SCRIPT_ACTIVE)
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def teste_remove_script_valid_inative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.ID_VALID)
        self._attr_invalid(response, CodeError.VLAN_INACTIVE)

    def test_remove_script_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.ID_REMOVE_SCRIPT_VALID)
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_remove_script_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE_SCRIPT % self.ID_REMOVE_SCRIPT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_script_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE_SCRIPT % self.ID_REMOVE_SCRIPT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_script_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_remove_script_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_remove_script_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_remove_script_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_remove_script_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_SCRIPT % self.EMPTY_ATTR)
        self._attr_invalid(response)


class VlanListPermissionTest(VlanConfigTest, AttrTest):

    def test_list_permission_valid(self):
        mock = self.mock_list_permission()
        response = self.client_autenticado().putXML(
            self.URL_LIST_PERMISSION, {'equipamento': mock})
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_list_permission_no_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_permission().putXML(
            self.URL_LIST_PERMISSION, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_list_permission_no_read_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_read_permission().putXML(
            self.URL_LIST_PERMISSION, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_list_permission_nonexistent_equipment(self):
        response = self.permission_script(
            self.URL_LIST_PERMISSION, "nome", 'EquipmentDoesNotExist')
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_list_permission_empty_equipment(self):
        response = self.permission_script(
            self.URL_LIST_PERMISSION, "nome", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_list_permission_none_equipment(self):
        response = self.permission_script(
            self.URL_LIST_PERMISSION, "nome", self.NONE_ATTR)
        self._attr_invalid(response)

    def test_list_permission_nonexistent_interface(self):
        response = self.permission_script(
            self.URL_LIST_PERMISSION, "nome_interface", 'InterfaceDoesNotExist')
        self._not_found(response, CodeError.INTERFACE_NOT_FOUND)

    def test_list_permission_empty_interface(self):
        response = self.permission_script(
            self.URL_LIST_PERMISSION, "nome_interface", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_list_permission_none_interface(self):
        response = self.permission_script(
            self.URL_LIST_PERMISSION, "nome_interface", self.NONE_ATTR)
        self._attr_invalid(response)


class VlanCheckPermissionTest(VlanConfigTest, AttrTest):

    def test_check_permission_valid(self):
        mock = self.mock_list_permission()
        response = self.client_autenticado().putXML(
            self.URL_CHECK_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_check_permission_no_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_permission().putXML(
            self.URL_CHECK_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_check_permission_no_read_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_read_permission().putXML(
            self.URL_CHECK_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_check_permission_id_nonexistent(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.VLAN_NOT_FOUND)

    def test_check_permission_id_negative(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_check_permission_id_zero(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_check_permission_id_empty(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_check_permission_id_none(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_check_permission_id_letter(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_check_permission_nonexistent_equipment(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ID_VALID, "nome", 'EquipmentDoesNotExist')
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_check_permission_empty_equipment(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ID_VALID, "nome", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_check_permission_none_equipment(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ID_VALID, "nome", self.NONE_ATTR)
        self._attr_invalid(response)

    def test_check_permission_nonexistent_interface(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ID_VALID, "nome_interface", 'InterfaceDoesNotExist')
        self._not_found(response, CodeError.INTERFACE_NOT_FOUND)

    def test_check_permission_empty_interface(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ID_VALID, "nome_interface", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_check_permission_none_interface(self):
        response = self.permission_script(
            self.URL_CHECK_PERMISSION % self.ID_VALID, "nome_interface", self.NONE_ATTR)
        self._attr_invalid(response)


class VlanAddPermissionTest(VlanConfigTest, AttrTest):

    def test_add_permission_valid(self):
        mock = self.mock_list_permission()
        response = self.client_autenticado().putXML(
            self.URL_ADD_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_add_permission_no_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_permission().putXML(
            self.URL_ADD_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_add_permission_no_read_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_read_permission().putXML(
            self.URL_ADD_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_add_permission_id_nonexistent(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.VLAN_NOT_FOUND)

    def test_add_permission_id_negative(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_add_permission_id_zero(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_add_permission_id_empty(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_add_permission_id_none(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_add_permission_id_letter(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_add_permission_nonexistent_equipment(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ID_VALID, "nome", 'EquipamentoDoesNotExist')
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_add_permission_empty_equipment(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ID_VALID, "nome", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_add_permission_none_equipment(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ID_VALID, "nome", self.NONE_ATTR)
        self._attr_invalid(response)

    def test_add_permission_nonexistent_interface(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ID_VALID, "nome_interface", 'InterfaceDoesNotExist')
        self._not_found(response, CodeError.INTERFACE_NOT_FOUND)

    def test_add_permission_empty_interface(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ID_VALID, "nome_interface", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_add_permission_none_interface(self):
        response = self.permission_script(
            self.URL_ADD_PERMISSION % self.ID_VALID, "nome_interface", self.NONE_ATTR)
        self._attr_invalid(response)


class VlanRemovePermissionTest(VlanConfigTest, AttrTest):

    def test_remove_permission_valid(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_VALID)
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_remove_permission_no_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_permission().putXML(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_permission_no_read_permission(self):
        mock = self.mock_list_permission()
        response = self.client_no_read_permission().putXML(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, {'equipamento': mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_permission_id_nonexistent(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.VLAN_NOT_FOUND)

    def test_remove_permission_id_negative(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_id_zero(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_id_empty(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_id_none(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_id_letter(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_nonexistent_equipment(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, "nome", "EquipmentDoesNotExist")
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_permission_empty_equipment(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, "nome", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_none_equipment(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, "nome", self.NONE_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_nonexistent_interface(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, "nome_interface", "InterfaceDoesNotExist")
        self._not_found(response, CodeError.INTERFACE_NOT_FOUND)

    def test_remove_permission_empty_interface(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, "nome_interface", self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_remove_permission_none_interface(self):
        response = self.permission_script(
            self.URL_REMOVE_PERMISSION % self.ID_VALID, "nome_interface", self.NONE_ATTR)
        self._attr_invalid(response)


class VlanGetByIdConsultationTest(VlanConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def test_get_by_id_valid_without_nets(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID % self.ID_VLAN_WITHOUT_NET)
        # Vlan must have network to return with success
        self._attr_invalid(response, CodeError.VLAN_HAS_NO_NETWORKS)

    def test_get_by_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID % self.ID_VALID_WITH_NET)
        valid_response(response)
        valid_content(response)

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


class VlanAllocateTest(VlanConfigTest, AttrTest):

    def test_allocate_valid(self):
        mock = self.mock_valid_allocate()
        response = self.client_autenticado().postXML(
            self.URL_ALLOCATE_VLAN, {self.XML_KEY: mock})
        valid_response(response)
        valid_content(response)

    def test_no_number_available_allocate(self):
        mock = self.mock_valid_allocate()
        mock['nome'] = 'VLAN_ALLOCATO_NO_NUMBER_AVAILABLE'
        response = self.client_autenticado().postXML(
            self.URL_ALLOCATE_VLAN, {self.XML_KEY: mock})
        self._attr_invalid(response, CodeError.VLANNUMBERNOTAVAILABLEERROR)

    def test_allocate_no_permission(self):
        mock = self.mock_valid_allocate()
        response = self.client_no_permission().postXML(
            self.URL_ALLOCATE_VLAN, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_allocate_no_write_permission(self):
        mock = self.mock_valid_allocate()
        response = self.client_no_write_permission().postXML(
            self.URL_ALLOCATE_VLAN, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_allocate_invalid_env_nonexistent(self):
        response = self.allocate_invalid('id_ambiente', self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_allocate_invalid_env_negative(self):
        response = self.allocate_invalid('id_ambiente', self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_env_empty(self):
        response = self.allocate_invalid('id_ambiente', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_env_none(self):
        response = self.allocate_invalid('id_ambiente', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_env_letter(self):
        response = self.allocate_invalid('id_ambiente', self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_nettype_nonexistent(self):
        response = self.allocate_invalid('id_tipo_rede', self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.NETWORK_TYPE_NOT_FOUND)

    def test_allocate_invalid_nettype_negative(self):
        response = self.allocate_invalid('id_tipo_rede', self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_nettype_empty(self):
        response = self.allocate_invalid('id_tipo_rede', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_nettype_none(self):
        response = self.allocate_invalid('id_tipo_rede', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_nettype_letter(self):
        response = self.allocate_invalid('id_tipo_rede', self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_vip_env_nonexistent(self):
        response = self.allocate_invalid(
            'id_ambiente_vip', self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_allocate_invalid_vip_env_negative(self):
        response = self.allocate_invalid('id_ambiente_vip', self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_vip_env_letter(self):
        response = self.allocate_invalid('id_ambiente_vip', self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_name_empty(self):
        response = self.allocate_invalid('nome', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_name_none(self):
        response = self.allocate_invalid('nome', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_invalid_name_maxsize(self):
        response = self.allocate_invalid('nome', string_generator(51))
        self._attr_invalid(response)

    def test_allocate_invalid_name_minsize(self):
        response = self.allocate_invalid('nome', string_generator(2))
        self._attr_invalid(response)

    def test_allocate_invalid_description_maxsize(self):
        response = self.allocate_invalid('descricao', string_generator(201))
        self._attr_invalid(response)

    def test_allocate_invalid_description_minsize(self):
        response = self.allocate_invalid('descricao', string_generator(2))
        self._attr_invalid(response)


class VlanAllocateV6(VlanConfigTest, AttrTest):

    def test_allocate_v6_valid(self):
        mock = self.mock_valid_allocate_v6()
        response = self.client_autenticado().postXML(
            self.URL_ALLOCATE_VLAN_V6, {self.XML_KEY: mock})
        valid_response(response)
        valid_content(response)

    def test_allocate_v6_no_permission(self):
        mock = self.mock_valid_allocate_v6()
        response = self.client_no_permission().postXML(
            self.URL_ALLOCATE_VLAN_V6, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_allocate_v6_no_write_permission(self):
        mock = self.mock_valid_allocate_v6()
        response = self.client_no_write_permission().postXML(
            self.URL_ALLOCATE_VLAN_V6, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_allocate_v6_invalid_env_nonexistent(self):
        response = self.allocate_invalid_v6(
            'id_environment', self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_allocate_v6_invalid_env_negative(self):
        response = self.allocate_invalid_v6(
            'id_environment', self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_env_empty(self):
        response = self.allocate_invalid_v6('id_environment', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_env_none(self):
        response = self.allocate_invalid_v6('id_environment', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_env_letter(self):
        response = self.allocate_invalid_v6('id_environment', self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_nettype_nonexistent(self):
        response = self.allocate_invalid_v6(
            'id_network_type', self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.NETWORK_TYPE_NOT_FOUND)

    def test_allocate_v6_invalid_nettype_negative(self):
        response = self.allocate_invalid_v6(
            'id_network_type', self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_nettype_empty(self):
        response = self.allocate_invalid_v6('id_network_type', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_nettype_none(self):
        response = self.allocate_invalid_v6('id_network_type', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_nettype_letter(self):
        response = self.allocate_invalid_v6(
            'id_network_type', self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_vip_env_nonexistent(self):
        response = self.allocate_invalid_v6(
            'id_environment_vip', self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_allocate_v6_invalid_vip_env_negative(self):
        response = self.allocate_invalid_v6(
            'id_environment_vip', self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_vip_env_letter(self):
        response = self.allocate_invalid_v6(
            'id_environment_vip', self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_name_empty(self):
        response = self.allocate_invalid_v6('name', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_name_none(self):
        response = self.allocate_invalid_v6('name', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_v6_invalid_name_maxsize(self):
        response = self.allocate_invalid_v6('name', string_generator(51))
        self._attr_invalid(response)

    def test_allocate_v6_invalid_name_minsize(self):
        response = self.allocate_invalid_v6('name', string_generator(2))
        self._attr_invalid(response)

    def test_allocate_v6_invalid_description_maxsize(self):
        response = self.allocate_invalid_v6(
            'description', string_generator(201))
        self._attr_invalid(response)

    def test_allocate_v6_invalid_description_minsize(self):
        response = self.allocate_invalid_v6('description', string_generator(2))
        self._attr_invalid(response)


class VlanAllocateNoNetworkTest(VlanConfigTest, AttrTest):

    def test_allocate_no_net_valid(self):
        mock = self.mock_valid_allocate_no_net()
        response = self.client_autenticado().postXML(
            self.URL_ALLOCATE_NO_NETWORK, {self.XML_KEY: mock})
        valid_response(response)
        valid_content(response)

    def test_allocate_no_net_no_permission(self):
        mock = self.mock_valid_allocate_no_net()
        response = self.client_no_permission().postXML(
            self.URL_ALLOCATE_NO_NETWORK, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_allocate_no_net_no_write_permission(self):
        mock = self.mock_valid_allocate_no_net()
        response = self.client_no_write_permission().postXML(
            self.URL_ALLOCATE_NO_NETWORK, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_allocate_no_net_invalid_env_nonexistent(self):
        response = self.allocate_invalid_no_net(
            'environment_id', self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_allocate_no_net_invalid_env_negative(self):
        response = self.allocate_invalid_no_net(
            'environment_id', self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_env_empty(self):
        response = self.allocate_invalid_no_net(
            'environment_id', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_env_none(self):
        response = self.allocate_invalid_no_net(
            'environment_id', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_env_letter(self):
        response = self.allocate_invalid_no_net(
            'environment_id', self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_name_empty(self):
        response = self.allocate_invalid_no_net('name', self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_name_none(self):
        response = self.allocate_invalid_no_net('name', self.NONE_ATTR)
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_name_minsize(self):
        response = self.allocate_invalid_no_net('name', string_generator(2))
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_name_maxsize(self):
        response = self.allocate_invalid_no_net('name', string_generator(51))
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_description_maxsize(self):
        response = self.allocate_invalid_no_net(
            'description', string_generator(201))
        self._attr_invalid(response)

    def test_allocate_no_net_invalid_description_minsize(self):
        response = self.allocate_invalid_no_net(
            'description', string_generator(2))
        self._attr_invalid(response)


class VlanCreateScriptTest(VlanConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def test_create_script_valid(self):
        response = self.client_autenticado().putXML(
            self.URL_CREATE_SCRIPT % self.ID_VALID, {'vlan': None})
        valid_response(response)
        content = valid_content(response, 'sucesso')
        assert int(content['codigo']) == 0

    def test_create_script_no_permission(self):
        response = self.client_no_permission().putXML(
            self.URL_CREATE_SCRIPT % self.ID_VALID, {'vlan': None})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_script_no_write_permission(self):
        response = self.client_no_write_permission().putXML(
            self.URL_CREATE_SCRIPT % self.ID_VALID, {'vlan': None})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_script_nonexistent(self):
        response = self.client_autenticado().putXML(
            self.URL_CREATE_SCRIPT % self.ID_NONEXISTENT, {'vlan': None})
        self._not_found(response)

    def test_create_script_negative(self):
        response = self.client_autenticado().putXML(
            self.URL_CREATE_SCRIPT % self.NEGATIVE_ATTR, {'vlan': None})
        self._attr_invalid(response)

    def test_create_script_letter(self):
        response = self.client_autenticado().putXML(
            self.URL_CREATE_SCRIPT % self.LETTER_ATTR, {'vlan': None})
        self._attr_invalid(response)

    def test_create_script_zero(self):
        response = self.client_autenticado().putXML(
            self.URL_CREATE_SCRIPT % self.ZERO_ATTR, {'vlan': None})
        self._attr_invalid(response)

    def test_create_script_empty(self):
        response = self.client_autenticado().putXML(
            self.URL_CREATE_SCRIPT % self.EMPTY_ATTR, {'vlan': None})
        self._attr_invalid(response)


class VlanCreateNetV4ScriptTest(VlanConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.NETWORK_IPV4_NOT_FOUND

    def test_create_script_valid(self):
        response = self.client_autenticado().postXML(self.URL_CREATE_SCRIPT_NET4, {
            self.XML_KEY: {'id_network_ip': self.ID_NETV4_CREATE_SCRIPT}})
        valid_response(response)
        content = valid_content(response, 'sucesso')
        vlan_success = content['vlan']
        net_success = content['network']
        assert int(vlan_success['codigo']) == 0
        assert int(net_success['codigo']) == 0

    def test_create_script_no_permission(self):
        response = self.client_no_permission().postXML(self.URL_CREATE_SCRIPT_NET4, {
            self.XML_KEY: {'id_network_ip': self.ID_NETV4_CREATE_SCRIPT}})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_script_no_write_permission(self):
        response = self.client_no_write_permission().postXML(
            self.URL_CREATE_SCRIPT_NET4, {self.XML_KEY: {'id_network_ip': self.ID_VALID}})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_script_nonexistent(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET4, {self.XML_KEY: {'id_network_ip': self.ID_NONEXISTENT}})
        self._not_found(response)

    def test_create_script_negative(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET4, {self.XML_KEY: {'id_network_ip': self.NEGATIVE_ATTR}})
        self._attr_invalid(response)

    def test_create_script_letter(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET4, {self.XML_KEY: {'id_network_ip': self.LETTER_ATTR}})
        self._attr_invalid(response)

    def test_create_script_zero(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET4, {self.XML_KEY: {'id_network_ip': self.ZERO_ATTR}})
        self._attr_invalid(response)

    def test_create_script_empty(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET4, {self.XML_KEY: {'id_network_ip': self.EMPTY_ATTR}})
        self._attr_invalid(response)


class VlanCreateNetV6ScriptTest(VlanConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.NETWORK_IPV6_NOT_FOUND

    def test_create_script_valid(self):
        response = self.client_autenticado().postXML(self.URL_CREATE_SCRIPT_NET6, {
            self.XML_KEY: {'id_network_ip': self.ID_NETV6_CREATE_SCRIPT}})
        valid_response(response)
        content = valid_content(response, 'sucesso')
        vlan_success = content['vlan']
        net_success = content['network']
        assert int(vlan_success['codigo']) == 0
        assert int(net_success['codigo']) == 0

    def test_create_script_no_permission(self):
        response = self.client_no_permission().postXML(self.URL_CREATE_SCRIPT_NET6, {
            self.XML_KEY: {'id_network_ip': self.ID_NETV6_CREATE_SCRIPT}})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_script_no_write_permission(self):
        response = self.client_no_write_permission().postXML(
            self.URL_CREATE_SCRIPT_NET6, {self.XML_KEY: {'id_network_ip': self.ID_VALID}})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_create_script_nonexistent(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET6, {self.XML_KEY: {'id_network_ip': self.ID_NONEXISTENT}})
        self._not_found(response)

    def test_create_script_negative(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET6, {self.XML_KEY: {'id_network_ip': self.NEGATIVE_ATTR}})
        self._attr_invalid(response)

    def test_create_script_letter(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET6, {self.XML_KEY: {'id_network_ip': self.LETTER_ATTR}})
        self._attr_invalid(response)

    def test_create_script_zero(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET6, {self.XML_KEY: {'id_network_ip': self.ZERO_ATTR}})
        self._attr_invalid(response)

    def test_create_script_empty(self):
        response = self.client_autenticado().postXML(
            self.URL_CREATE_SCRIPT_NET6, {self.XML_KEY: {'id_network_ip': self.EMPTY_ATTR}})
        self._attr_invalid(response)


@me
class VlanAttrNetworkTypeTest(VlanConfigTest, AttrTest):

    def test_add_automatic_network_type_ipv4_invalid_option(self):
        mock = self.mock_valid()
        mock['network_ipv4'] = 2
        self.process_save_attr_invalid(mock)

    def test_add_automatic_network_type_ipv6_invalid_option(self):
        mock = self.mock_valid()
        mock['network_ipv6'] = 2
        self.process_save_attr_invalid(mock)

    def test_add_automatic_network_type_ipv4_config_environment_not_exist(self):
        mock = self.mock_valid()
        mock['network_ipv4'] = 1
        mock["environment_id"] = 29
        self.process_save_attr_invalid(mock, 294)

    def test_add_automatic_network_type_ipv6_config_environment_not_exist(self):
        mock = self.mock_valid()
        mock['network_ipv6'] = 1
        mock["environment_id"] = 29
        self.process_save_attr_invalid(mock, 294)

    def test_add_automatic_network_type_ipv4_success(self):
        mock = self.mock_valid()
        mock['network_ipv4'] = 1
        mock["environment_id"] = 30
        self.process_save_attr_invalid(mock)

    def test_add_automatic_network_type_ipv6_success(self):
        mock = self.mock_valid()
        mock['network_ipv6'] = 1
        mock["environment_id"] = 30
        self.process_save_attr_invalid(mock)
