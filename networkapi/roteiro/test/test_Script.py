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
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.roteiro.models import Roteiro
from networkapi.test import BasicTestCase, CodeError, ConsultationTest, me, RemoveTest, AttrTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator, valid_get_filtered
import httplib


class ScriptConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/roteiro/fixtures/initial_data.yaml']
    XML_KEY = "script"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    OBJ = Roteiro

    # Urls
    URL_SAVE = "/script/"
    URL_ALTER = "/script/%s/"
    URL_REMOVE = "/script/%s/"
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/script/all/"
    URL_GET_SCRIPT_TYPE = "/script/scripttype/%s/"
    URL_GET_EQUIPMENT = "/script/equipment/%s/"

    def mock_valid(self):
        mock = {}
        mock['script'] = 'mock'
        mock['description'] = 'description'
        mock['id_script_type'] = 4
        return mock

    def valid_attr(self, mock, obj):
        assert mock["script"] == obj["roteiro"]
        assert mock["description"] == obj["descricao"]
        assert mock["id_script_type"] == int(obj["tipo_roteiro"])


class ScriptConsultationTest(ScriptConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.SCRIPT_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script")
        valid_get_all(content, self.OBJ)

    def test_get_all_inactive(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response, httplib.UNAUTHORIZED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class ScriptTest(ScriptConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        script = valid_content(response, "script")

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script")

        for scr in content:
            if scr["id"] == script["id"]:
                self.valid_attr(mock, scr)
                break

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
        mock = self.mock_valid()
        mock["script"] = "ScriptAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script")

        for scr in content:
            if scr["id"] == self.ID_ALTER_VALID:
                self.valid_attr(mock, scr)
                break

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class ScriptRemoveTest(ScriptConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.SCRIPT_NOT_FOUND

    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_script_related(self):
        response = self.remove(self.ID_VALID)
        self._attr_invalid(response, CodeError.SCRIPT_RELATED)

    def test_remove_by_id_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_by_id_negative(self):
        self.remove_negative()

    def test_remove_by_id_letter(self):
        self.remove_letter()

    def test_remove_by_id_zero(self):
        self.remove_zero()

    def test_remove_by_id_empty(self):
        self.remove_empty()


@me
class ScriptAttrTypeTest(ScriptConfigTest, AttrTest):

    KEY_ATTR = "script"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(41)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'Script'
        mock["id_script_type"] = 1
        self.process_save_attr_invalid(mock, CodeError.SCRIPT_DUPLICATE)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(41)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_unique(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'Script'
        mock['id_script_type'] = 1
        self.process_alter_attr_invalid(
            self.ID_ALTER_VALID, mock, CodeError.SCRIPT_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class ScriptAttrDescriptionTest(ScriptConfigTest, AttrTest):

    KEY_ATTR = "description"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
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
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class ScriptAttrScriptTypeTest(ScriptConfigTest, AttrTest):

    KEY_ATTR = "id_script_type"
    CODE_ERROR_NOT_FOUND = CodeError.SCRIPT_TYPE_NOT_FOUND

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
        self.alter_attr_nonexistent(self.ID_ALTER_VALID)

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ID_ALTER_VALID)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class ScriptConsultationScriptTypeTest(ScriptConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.SCRIPT_TYPE_NOT_FOUND

    def test_get_by_script_type(self):
        response = self.client_autenticado().get(
            self.URL_GET_SCRIPT_TYPE % self.ID_VALID)
        valid_response(response)
        content = valid_content(response, "script", True)

        query = Q(tipo_roteiro__id=self.ID_VALID)
        valid_get_filtered(content, self.OBJ, query)

    def test_get_by_script_type_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_SCRIPT_TYPE % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_script_type_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_SCRIPT_TYPE % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_script_type_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_SCRIPT_TYPE % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_script_type_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_SCRIPT_TYPE % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_script_type_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_SCRIPT_TYPE % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_script_type_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_SCRIPT_TYPE % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_script_type_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_SCRIPT_TYPE % self.EMPTY_ATTR)
        self._attr_invalid(response)


class ScriptConsultationEquipmentTest(ScriptConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_get_by_equipment(self):
        response = self.client_autenticado().get(
            self.URL_GET_EQUIPMENT % self.ID_VALID)
        valid_response(response)
        content = valid_content(response, "script", True)

        query = Q(equipamento__id=self.ID_VALID)
        valid_get_filtered(content, EquipamentoRoteiro, query)

    def test_get_by_equipment_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_EQUIPMENT % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_EQUIPMENT % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_EQUIPMENT % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_equipment_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_EQUIPMENT % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_EQUIPMENT % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_EQUIPMENT % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_EQUIPMENT % self.EMPTY_ATTR)
        self._attr_invalid(response)
