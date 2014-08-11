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
from networkapi.ambiente.models import Ambiente
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, \
    RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, \
    valid_get_all, valid_get_filtered, string_generator
import httplib


class EnvironmentConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/ambiente/fixtures/initial_data.yaml']
    XML_KEY = "ambiente"

    OBJ = Ambiente

    ID_VALID = 1
    ID_REMOVE_VALID = 2
    ID_ALTER_VALID = 3

    ID_REMOVE_EVIRONMENT = 4
    ID_REMOVE_CONFIG = 2

    ID_EQUIPMENT_VALID = 1
    ID_DIVISION_DC_VALID = 1
    ID_ENVIRONMENT_LOGICAL_VALID = 1
    ID_IP_CONFIG_VALID = 1

    # Urls
    URL_SAVE = "/ambiente/"
    URL_SAVE_ENVIRONMENT_IPCONFIG = "/ambiente/ipconfig/"
    URL_SAVE_IPCONFIG = "/ipconfig/"
    URL_ALTER = "/ambiente/%s/"
    URL_REMOVE = "/ambiente/%s/"
    URL_GET_ALL = "/ambiente/list/"
    URL_GET_ALL_2 = "/ambiente/"
    URL_GET_BY_ENV_ID = "/environment/id/%s/"
    URL_GET_BY_EQUIP = "/ambiente/equip/%s/"
    URL_GET_BY_EQUIP_IP = "/ambiente/equipamento/%s/ip/%s/"
    URL_GET_BY_DIVISAO_DC = "/ambiente/divisao_dc/%s/"
    URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT = "/ambiente/divisao_dc/%s/ambiente_logico/%s/"
    URL_SAVE_ENVIRONMENT_CONFIGURATION = "/environment/configuration/save/"
    URL_LIST_ENVIRONMENT_CONFIGURATION = "/environment/configuration/list/%s/"
    URL_REMOVE_ENVIRONMENT_CONFIGURATION = "/environment/configuration/remove/%s/%s/"

    def mock_valid(self):
        mock = {}
        mock['id_grupo_l3'] = 2
        mock['id_ambiente_logico'] = 1
        mock['id_divisao'] = 1
        mock['link'] = "NEW-LINK"
        mock['id_filter'] = 1
        mock['min_num_vlan_1'] = 1
        mock['max_num_vlan_1'] = 10
        mock['min_num_vlan_2'] = 11
        mock['max_num_vlan_2'] = 20

        return mock

    def mock_valid_alter(self):
        mock = {}
        mock['id_ambiente'] = 3
        mock['id_grupo_l3'] = 3
        mock['id_ambiente_logico'] = 3
        mock['id_divisao'] = 3
        mock['link'] = "LINKALTER"
        mock['id_filter'] = 1
        mock['min_num_vlan_1'] = 100
        mock['max_num_vlan_1'] = 200
        mock['min_num_vlan_2'] = 201
        mock['max_num_vlan_2'] = 300
        return mock

    def mock_ip_config_valid(self):
        mock = {}
        mock['id_environment'] = 1
        mock['id_ip_config'] = 1
        return mock

    def mock_environment_ip_config_valid(self):
        mock = {}
        mock['id_grupo_l3'] = 3
        mock['id_ambiente_logico'] = 1
        mock['id_divisao'] = 1
        mock['id_filter'] = 1
        mock['id_ip_config'] = 1
        mock['link'] = "NEW-LINK-ENV-IP-CONFIG"
        return mock

    def mock_environment_configuration_v4(self):

        mock = dict({

            'network': '192.168.0.0/16',
            'id_environment': 1,
            'ip_version': 'v4',
            'prefix': 24,
            'network_type': 1
        })

        return mock

    def mock_environment_configuration_v6(self):

        mock = dict({

            'network': 'ffff:ffff:ffff:ffff:ffff:ffff:0:0/96',
            'id_environment': 1,
            'ip_version': 'v6',
            'prefix': 112,
            'network_type': 1
        })

        return mock

    def valid_attr(self, mock, obj):
        assert mock["id_grupo_l3"] == obj["grupo_l3"]
        assert mock["id_ambiente_logico"] == obj["ambiente_logico"]
        assert mock["id_divisao"] == obj["divisao_dc"]
        assert mock["link"] == obj["link"]
        assert mock["id_filter"] == obj["filter"]

    def env_ip_config_attr_test(self, attr):
        mock = self.mock_environment_ip_config_valid()
        mock[self.KEY_ATTR] = attr
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_IPCONFIG, {self.XML_KEY: mock})
        return response


class EnvironmentConsultationTest(EnvironmentConfigTest, ConsultationTest):

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_KEY, True)
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_2(self):
        response = self.client_autenticado().get(self.URL_GET_ALL_2)
        valid_response(response)
        content = valid_content(response, self.XML_KEY, True)
        valid_get_all(content, self.OBJ)

    def test_get_all_2_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_ALL_2)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_2_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_ALL_2)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EnvironmentConsultationEnvironmentTest(EnvironmentConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENVIRONMENT_NOT_FOUND

    def test_get_by_environment(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID % self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY, True)

    def test_get_by_environment_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ENV_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ENV_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_environment_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID % self.EMPTY_ATTR)
        self._attr_invalid(response)


class EnvironmentConsultationDivisionDcTest(EnvironmentConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.DIVISION_DC_NOT_FOUND

    def test_get_by_division(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_DIVISAO_DC % self.ID_DIVISION_DC_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY, True)

    def test_get_by_division_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_DIVISAO_DC % self.ID_DIVISION_DC_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_division_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_DIVISAO_DC % self.ID_DIVISION_DC_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_division_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_DIVISAO_DC % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_division_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_DIVISAO_DC % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_division_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_DIVISAO_DC % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_division_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_DIVISAO_DC % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_division_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_DIVISAO_DC % self.EMPTY_ATTR)
        self._attr_invalid(response)


class EnvironmentConsultationDivisionDcEnvironmentLogicalTest(EnvironmentConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.DIVISION_DC_NOT_FOUND

    def test_get_by_division_environment_logical(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_DIVISION_DC_VALID, self.ID_ENVIRONMENT_LOGICAL_VALID))
        valid_response(response)
        valid_content(response, self.XML_KEY, True)

    def test_get_by_division_environment_logical_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                   (self.ID_DIVISION_DC_VALID, self.ID_ENVIRONMENT_LOGICAL_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_division_environment_logical_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                        (self.ID_DIVISION_DC_VALID, self.ID_ENVIRONMENT_LOGICAL_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_division_environment_logical_nonexistent(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_NONEXISTENT, self.ID_ENVIRONMENT_LOGICAL_VALID))
        self._not_found(response)

    def test_get_by_division_environment_logical_negative(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.NEGATIVE_ATTR, self.ID_ENVIRONMENT_LOGICAL_VALID))
        self._attr_invalid(response)

    def test_get_by_division_environment_logical_letter(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.LETTER_ATTR, self.ID_ENVIRONMENT_LOGICAL_VALID))
        self._attr_invalid(response)

    def test_get_by_division_environment_logical_zero(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ZERO_ATTR, self.ID_ENVIRONMENT_LOGICAL_VALID))
        self._attr_invalid(response)

    def test_get_by_division_environment_logical_empty(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.EMPTY_ATTR, self.ID_ENVIRONMENT_LOGICAL_VALID))
        self._attr_invalid(response)


class EnvironmentConsultationEnvironmentLogicalDivisionDcTest(EnvironmentConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.LOGICAL_ENVIRONMENT_NOT_FOUND

    def test_get_by_environment_logical_division(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_DIVISION_DC_VALID, self.ID_ENVIRONMENT_LOGICAL_VALID))
        valid_response(response)
        valid_content(response, self.XML_KEY, True)

    def test_get_by_environment_logical_division_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                   (self.ID_DIVISION_DC_VALID, self.ID_ENVIRONMENT_LOGICAL_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_logical_division_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                        (self.ID_DIVISION_DC_VALID, self.ID_ENVIRONMENT_LOGICAL_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_logical_division_nonexistent(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_DIVISION_DC_VALID, self.ID_NONEXISTENT))
        self._not_found(response)

    def test_get_by_environment_logical_division_negative(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_DIVISION_DC_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_get_by_environment_logical_division_letter(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_DIVISION_DC_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_get_by_environment_logical_division_zero(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_DIVISION_DC_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_get_by_environment_logical_division_empty(self):
        response = self.client_autenticado().get(self.URL_GET_BY_DIVISAO_DC_LOGICAL_ENVIRONMENT %
                                                 (self.ID_DIVISION_DC_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)


class EnvironmentConsultationEquipmentTest(EnvironmentConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_get_by_equipment(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP % self.ID_EQUIPMENT_VALID)
        valid_response(response)
        content = valid_content(response, self.XML_KEY, True)
        query = Q(equipamentoambiente__equipamento=self.ID_EQUIPMENT_VALID)
        valid_get_filtered(content, Ambiente, query)

    def test_get_by_equipment_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_EQUIP % self.ID_EQUIPMENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_EQUIP % self.ID_EQUIPMENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_equipment_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP % self.EMPTY_ATTR)
        self._attr_invalid(response)


class EnvironmentTest(EnvironmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY)

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
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)
        environ = Ambiente.get_by_pk(self.ID_ALTER_VALID)
        self.valid_attr(mock, model_to_dict(environ))

    def test_alter_no_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EnvironmentAttrGrupoL3Test(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_grupo_l3"
    CODE_ERROR_NOT_FOUND = CodeError.GROUP_L3_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

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
        self.alter_attr_nonexistent(self.ID_NONEXISTENT)

    def test_alter_negative(self):
        self.alter_attr_negative(self.NEGATIVE_ATTR)

    def test_alter_letter(self):
        self.alter_attr_letter(self.LETTER_ATTR)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ZERO_ATTR)

    def test_alter_empty(self):
        self.alter_attr_empty(self.EMPTY_ATTR)

    def test_alter_none(self):
        self.alter_attr_none(self.NONE_ATTR)


class EnvironmentAttrLogicalEnvironmentTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_ambiente_logico"
    CODE_ERROR_NOT_FOUND = CodeError.LOGICAL_ENVIRONMENT_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

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
        self.alter_attr_nonexistent(self.ID_NONEXISTENT)

    def test_alter_negative(self):
        self.alter_attr_negative(self.NEGATIVE_ATTR)

    def test_alter_letter(self):
        self.alter_attr_letter(self.LETTER_ATTR)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ZERO_ATTR)

    def test_alter_empty(self):
        self.alter_attr_empty(self.EMPTY_ATTR)

    def test_alter_none(self):
        self.alter_attr_none(self.NONE_ATTR)


class EnvironmentAttrDivisionTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_divisao"
    CODE_ERROR_NOT_FOUND = CodeError.DIVISION_DC_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

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
        self.alter_attr_nonexistent(self.ID_NONEXISTENT)

    def test_alter_negative(self):
        self.alter_attr_negative(self.NEGATIVE_ATTR)

    def test_alter_letter(self):
        self.alter_attr_letter(self.LETTER_ATTR)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ZERO_ATTR)

    def test_alter_empty(self):
        self.alter_attr_empty(self.EMPTY_ATTR)

    def test_alter_none(self):
        self.alter_attr_none(self.NONE_ATTR)


class EnvironmentAttrLinkTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "link"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_save_attr_invalid(mock)

    def test_alter_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)


class EnvironmentAttrFilterTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_filter"
    CODE_ERROR_NOT_FOUND = CodeError.FILTER_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_alter_nonexistent(self):
        self.alter_attr_nonexistent(self.ID_NONEXISTENT)

    def test_alter_negative(self):
        self.alter_attr_negative(self.NEGATIVE_ATTR)

    def test_alter_letter(self):
        self.alter_attr_letter(self.LETTER_ATTR)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ZERO_ATTR)


class EnvironmentRemoveTest(EnvironmentConfigTest, RemoveTest):

    def test_remove_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE % self.ID_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE % self.ID_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_environment_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_remove_environment_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_remove_environment_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_remove_environment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_remove_environment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_remove_environment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.NONE_ATTR)
        self._attr_invalid(response)


class IpConfigTest(EnvironmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_ip_config_valid()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, 'config_do_ambiente')

    def test_save_no_permission(self):
        mock = self.mock_ip_config_valid()
        response = self.client_no_permission().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_ip_config_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class IpConfigAttrEnvironmentTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_environment"
    CODE_ERROR_NOT_FOUND = CodeError.ENVIRONMENT_NOT_FOUND
    CodeError.CONFIG_ENVIRONMENT_ALREADY_EXISTS

    def test_save_nonexistent(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_duplicate(self):
        mock = self.mock_ip_config_valid()
        self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(
            response, CodeError.CONFIG_ENVIRONMENT_ALREADY_EXISTS)


class IpConfigAttrIpConfigTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_ip_config"
    CODE_ERROR_NOT_FOUND = CodeError.IP_CONFIG_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ip_config_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)


class EnvironmentIpConfigTest(EnvironmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_environment_ip_config_valid()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_IPCONFIG, {self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_save_no_permission(self):
        mock = self.mock_environment_ip_config_valid()
        response = self.client_no_permission().postXML(
            self.URL_SAVE_ENVIRONMENT_IPCONFIG, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_environment_ip_config_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_SAVE_ENVIRONMENT_IPCONFIG, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EnvironmentIpConfigAttrGrupoL3Test(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_grupo_l3"
    CODE_ERROR_NOT_FOUND = CodeError.GROUP_L3_NOT_FOUND

    def test_save_nonexistent(self):
        self._not_found(self.env_ip_config_attr_test(self.ID_NONEXISTENT))

    def test_save_negative(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NEGATIVE_ATTR))

    def test_save_letter(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.LETTER_ATTR))

    def test_save_zero(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.ZERO_ATTR))

    def test_save_empty(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.EMPTY_ATTR))

    def test_save_none(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NONE_ATTR))


class EnvironmentIpConfigAttrEnvironmentLogicalTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_ambiente_logico"
    CODE_ERROR_NOT_FOUND = CodeError.LOGICAL_ENVIRONMENT_NOT_FOUND

    def test_save_nonexistent(self):
        self._not_found(self.env_ip_config_attr_test(self.ID_NONEXISTENT))

    def test_save_negative(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NEGATIVE_ATTR))

    def test_save_letter(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.LETTER_ATTR))

    def test_save_zero(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.ZERO_ATTR))

    def test_save_empty(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.EMPTY_ATTR))

    def test_save_none(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NONE_ATTR))


class EnvironmentIpConfigAttrDivisionTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_divisao"
    CODE_ERROR_NOT_FOUND = CodeError.DIVISION_DC_NOT_FOUND

    def test_save_nonexistent(self):
        self._not_found(self.env_ip_config_attr_test(self.ID_NONEXISTENT))

    def test_save_negative(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NEGATIVE_ATTR))

    def test_save_letter(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.LETTER_ATTR))

    def test_save_zero(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.ZERO_ATTR))

    def test_save_empty(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.EMPTY_ATTR))

    def test_save_none(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NONE_ATTR))


class EnvironmentIpConfigAttrFilterTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_filter"
    CODE_ERROR_NOT_FOUND = CodeError.FILTER_NOT_FOUND

    def test_save_nonexistent(self):
        self._not_found(self.env_ip_config_attr_test(self.ID_NONEXISTENT))

    def test_save_negative(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NEGATIVE_ATTR))

    def test_save_letter(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.LETTER_ATTR))

    def test_save_zero(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.ZERO_ATTR))


class EnvironmentIpConfigAttrIpConfigTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "id_ip_config"
    CODE_ERROR_NOT_FOUND = CodeError.IP_CONFIG_NOT_FOUND

    def test_save_nonexistent(self):
        self._not_found(self.env_ip_config_attr_test(self.ID_NONEXISTENT))

    def test_save_negative(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NEGATIVE_ATTR))

    def test_save_letter(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.LETTER_ATTR))

    def test_save_zero(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.ZERO_ATTR))

    def test_save_empty(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.EMPTY_ATTR))

    def test_save_none(self):
        self._attr_invalid(self.env_ip_config_attr_test(self.NONE_ATTR))


class EnvironmentIpConfigAttrLinkTest(EnvironmentConfigTest, AttrTest):

    KEY_ATTR = "link"

    def test_save_maxsize(self):
        mock = self.mock_environment_ip_config_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_IPCONFIG, {self.XML_KEY: mock})
        self._attr_invalid(response)


@me
class EnvironmentConfigurationAddTest(EnvironmentConfigTest, AttrTest):

    def test_save_v4_valid(self):
        mock = self.mock_environment_configuration_v4()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        valid_response(response)

    def test_save_v6_valid(self):
        mock = self.mock_environment_configuration_v6()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        valid_response(response)

    def test_save_v4_no_permission(self):
        mock = self.mock_environment_configuration_v4()
        response = self.client_no_permission().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_v6_no_permission(self):
        mock = self.mock_environment_configuration_v6()
        response = self.client_no_permission().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_v4_invalid(self):
        mock = self.mock_environment_configuration_v4()
        mock.update({'network': '192.168.256.1/24'})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_v6_invalid(self):
        mock = self.mock_environment_configuration_v6()
        mock.update({'network': 'ffff:ffff:ffff:ffff:ffff:ffff:0101:0/96'})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_v4_invalid_prefix(self):
        mock = self.mock_environment_configuration_v4()
        mock.update({'network': '192.168.0.0/33'})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_v6_invalid_prefix(self):
        mock = self.mock_environment_configuration_v6()
        mock.update({'network': 'ffff:ffff:ffff:ffff:ffff:ffff:0:0/129'})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_v4_invalid_network_type(self):
        mock = self.mock_environment_configuration_v4()
        mock.update({'network_type': '0'})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_v6_invalid_network_type(self):
        mock = self.mock_environment_configuration_v6()
        mock.update({'network_type': '0'})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_nonexistent_environment(self):
        mock = self.mock_environment_configuration_v4()
        mock.update({'id_environment': self.ID_NONEXISTENT})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_save_invalid_environment(self):
        mock = self.mock_environment_configuration_v4()
        mock.update({'id_environment': self.LETTER_ATTR})
        response = self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock})
        self._attr_invalid(response)


class EnvironmentConfigurationListTest(EnvironmentConfigTest, AttrTest):

    def setUp(self):
        mock_v4 = self.mock_environment_configuration_v4()
        self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock_v4})
        mock_v6 = self.mock_environment_configuration_v6()
        self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock_v6})
        EnvironmentConfigTest.setUp(self)

    def test_get_all(self):
        response = self.client_autenticado().get(
            self.URL_LIST_ENVIRONMENT_CONFIGURATION % self.ID_VALID)
        lists_configuration = valid_content(
            response, 'lists_configuration', True)
        self.assertTrue(len(lists_configuration) == 2)

    def test_get_all_by_nonexistent_environment(self):
        response = self.client_autenticado().get(
            self.URL_LIST_ENVIRONMENT_CONFIGURATION % self.ID_NONEXISTENT)
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_get_all_by_invalid_environment(self):
        response = self.client_autenticado().get(
            self.URL_LIST_ENVIRONMENT_CONFIGURATION % self.LETTER_ATTR)
        self._attr_invalid(response)


class EnvironmentConfigurationRemoveTest(EnvironmentConfigTest, AttrTest):

    def setUp(self):
        mock_v4 = self.mock_environment_configuration_v4()
        self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock_v4})
        mock_v6 = self.mock_environment_configuration_v6()
        self.client_autenticado().postXML(
            self.URL_SAVE_ENVIRONMENT_CONFIGURATION, {self.XML_KEY: mock_v6})
        EnvironmentConfigTest.setUp(self)

    def test_remove(self):
        ENVIRONMENT_ID = self.ID_REMOVE_EVIRONMENT
        CONFIGURATION_ID = self.ID_REMOVE_CONFIG
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ENVIRONMENT_CONFIGURATION % (ENVIRONMENT_ID, CONFIGURATION_ID))
        valid_response(response)

    def test_remove_nonexistent(self):
        ENVIRONMENT_ID = self.ID_VALID
        CONFIGURATION_ID = self.ID_NONEXISTENT
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ENVIRONMENT_CONFIGURATION % (ENVIRONMENT_ID, CONFIGURATION_ID))
        self._attr_invalid(response, CodeError.IP_CONFIG_NOT_FOUND)

    def test_remove_invalid(self):
        ENVIRONMENT_ID = self.ID_VALID
        CONFIGURATION_ID = self.LETTER_ATTR
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ENVIRONMENT_CONFIGURATION % (ENVIRONMENT_ID, CONFIGURATION_ID))
        self._attr_invalid(response)

    def test_remove_environment_nonexistent(self):
        ENVIRONMENT_ID = self.ID_NONEXISTENT
        CONFIGURATION_ID = 22
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ENVIRONMENT_CONFIGURATION % (ENVIRONMENT_ID, CONFIGURATION_ID))
        self._attr_invalid(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_remove_environment_invalid(self):
        ENVIRONMENT_ID = 23
        CONFIGURATION_ID = self.LETTER_ATTR
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ENVIRONMENT_CONFIGURATION % (ENVIRONMENT_ID, CONFIGURATION_ID))
        self._attr_invalid(response,)
