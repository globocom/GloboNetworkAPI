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


from django.forms.models import model_to_dict
from django.db.models import Q
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator, valid_get_filtered
import httplib


class EquipmentAccessConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/tipoacesso/fixtures/initial_data.yaml']
    XML_KEY = "equipamento_acesso"
    ID_VALID = 1
    ID_ALTER_VALID = 1
    OBJ = EquipamentoAcesso

    ID_EQUIPMENT = 1
    ID_ACCESS = 1

    EQUIPMENT_NAME_VALID = "Balanceador de Teste"

    # Urls
    URL_SAVE = "/equipamentoacesso/"
    URL_ALTER = "/equipamentoacesso/edit/"
    URL_REMOVE = "/equipamentoacesso/%s/%s/"
    URL_GET_ALL = "/equipamentoacesso/"
    URL_GET_BY_EQUIP_NAME = "/equipamentoacesso/name/"
    URL_GET_BY_EQUIP_ACCESS_ID = "/equipamentoacesso/id/%s/"

    def mock_valid(self):
        mock = {}
        mock['id_equipamento'] = 2
        mock['id_tipo_acesso'] = 1
        mock['fqdn'] = "s41globoicom1"
        mock['user'] = "admin"
        mock['pass'] = "1234"
        mock['enable_pass'] = "1234"
        mock['protocolo_tipo_acesso'] = "1234"
        return mock

    def mock_valid_alter(self):
        mock = {}
        mock['id_equipamento'] = 1
        mock['id_equip_acesso'] = 1
        mock['id_tipo_acesso'] = 1
        mock['fqdn'] = "fqdnAlter"
        mock['user'] = "admin"
        mock['pass'] = "1234"
        mock['enable_pass'] = "1234"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["id_equipamento"] == obj["equipamento"]
        assert mock["id_tipo_acesso"] == obj["tipo_acesso"]
        assert mock["fqdn"] == obj["fqdn"]
        assert mock["user"] == obj["user"]
        assert mock["pass"] == obj["password"]
        assert mock["enable_pass"] == obj["enable_pass"]

    def process_alter_attr_invalid(self, idt, mock, code_error=None):
        response = self.client_autenticado().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        if code_error is not None:
            self._attr_invalid(response, code_error)
        else:
            self._attr_invalid(response)


class EquipmentAccessConsultationTest(EquipmentAccessConfigTest, ConsultationTest):

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


class EquipmentAccessConsultationEquipmentTest(EquipmentAccessConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_get_by_equipment(self):
        equip_access_map = dict()
        equip_access_map['name'] = self.EQUIPMENT_NAME_VALID

        response = self.client_autenticado().postXML(
            self.URL_GET_BY_EQUIP_NAME, {self.XML_KEY: equip_access_map})
        valid_response(response)
        content = valid_content(response, self.XML_KEY, True)
        query = Q(equipamento__nome=self.EQUIPMENT_NAME_VALID)
        valid_get_filtered(content, EquipamentoAcesso, query)

    def test_get_by_equipment_no_permission(self):
        equip_access_map = dict()
        equip_access_map['name'] = self.EQUIPMENT_NAME_VALID

        response = self.client_no_permission().postXML(
            self.URL_GET_BY_EQUIP_NAME, {self.XML_KEY: equip_access_map})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_no_read_permission(self):
        equip_access_map = dict()
        equip_access_map['name'] = self.EQUIPMENT_NAME_VALID

        response = self.client_no_read_permission().postXML(
            self.URL_GET_BY_EQUIP_NAME, {self.XML_KEY: equip_access_map})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentAccessConsultationEquipmentAccessTest(EquipmentAccessConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_ACCESS_NOT_FOUND

    def test_get_by_equipment_access(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.ID_VALID)
        valid_response(response)
        content = valid_content(response, self.XML_KEY, True)

        query = Q(equipamento__id=self.ID_VALID)
        valid_get_filtered(content, self.OBJ, query)

    def test_get_by_equipment_access_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_access_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_access_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_equipment_access_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_access_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_access_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_access_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_ACCESS_ID % self.EMPTY_ATTR)
        self._attr_invalid(response)


class EquipmentAccessTest(EquipmentAccessConfigTest):

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
        response = self.client_autenticado().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response)
        tpa = EquipamentoAcesso.get_by_pk(self.ID_ALTER_VALID)
        self.valid_attr(mock, model_to_dict(tpa))

    def test_alter_no_permission(self):
        mock = self.mock_valid_alter()
        response = self.client_no_permission().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid_alter()
        response = self.client_no_write_permission().postXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentAccessAttrEquipmentTest(EquipmentAccessConfigTest, AttrTest):

    KEY_ATTR = "id_equipamento"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

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


class EquipmentAccessAttrAccessTest(EquipmentAccessConfigTest, AttrTest):

    KEY_ATTR = "id_tipo_acesso"
    CODE_ERROR_NOT_FOUND = CodeError.ACCESS_TYPE_NOT_FOUND

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


class EquipmentAccessAttrFqdnTest(EquipmentAccessConfigTest, AttrTest):

    KEY_ATTR = "fqdn"

    def test_save_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(3)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(3)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class EquipmentAccessAttrUserTest(EquipmentAccessConfigTest, AttrTest):

    KEY_ATTR = "user"

    def test_save_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(21)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(21)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class EquipmentAccessAttrPassTest(EquipmentAccessConfigTest, AttrTest):

    KEY_ATTR = "pass"

    def test_save_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(151)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(151)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class EquipmentAccessAttrEnablePassTest(EquipmentAccessConfigTest, AttrTest):

    KEY_ATTR = "enable_pass"

    def test_save_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(151)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(151)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class EquipmentAccessRemoveTest(EquipmentAccessConfigTest, RemoveTest):

    def test_remove_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_ACCESS))
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_ACCESS))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_ACCESS))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_equipment_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_NONEXISTENT, self.ID_ACCESS))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_equipment_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.NEGATIVE_ATTR, self.ID_ACCESS))
        self._attr_invalid(response)

    def test_remove_equipment_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.LETTER_ATTR, self.ID_ACCESS))
        self._attr_invalid(response)

    def test_remove_equipment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ZERO_ATTR, self.ID_ACCESS))
        self._attr_invalid(response)

    def test_remove_equipment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.EMPTY_ATTR, self.ID_ACCESS))
        self._attr_invalid(response)

    def test_remove_equipment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.NONE_ATTR, self.ID_ACCESS))
        self._attr_invalid(response)

    def test_remove_access_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.ACCESS_TYPE_NOT_FOUND)

    def test_remove_access_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_remove_access_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_remove_access_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_remove_access_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_remove_access_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.NONE_ATTR))
        self._attr_invalid(response)
