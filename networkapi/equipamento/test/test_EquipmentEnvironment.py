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


from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.test import BasicTestCase, AttrTest, CodeError, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response
import httplib


class EquipmentEnvironmentConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/equipamento/fixtures/initial_data.yaml']
    XML_KEY = "equipamento_ambiente"
    ID_EQUIPMENT = 1
    ID_ENVIRONMENT = 1
    ID_EQUIPMENT_VALID = 2
    ID_ENVIRONMENT_VALID = 1
    OBJ = EquipamentoAmbiente

    # Urls
    URL_SAVE = "/equipamentoambiente/"
    URL_UPDATE = "/equipamentoambiente/update/"
    URL_REMOVE = "/equipment/%s/environment/%s/"

    def mock_valid(self):
        mock = {}
        mock['id_equipamento'] = 2
        mock['id_ambiente'] = 1
        mock['is_router'] = 0
        return mock

    def mock_update(self):
        mock = {}
        mock['id_equipamento'] = self.ID_EQUIPMENT
        mock['id_ambiente'] = self.ID_ENVIRONMENT
        mock['is_router'] = 1
        return mock

    def mock_nonexistent(self):
        mock = {}
        mock['id_equipamento'] = self.ID_NONEXISTENT
        mock['id_ambiente'] = self.ID_NONEXISTENT
        mock['is_router'] = 1
        return mock


class EquipmentEnvironmentTest(EquipmentEnvironmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        equipment_type = valid_content(response, self.XML_KEY)
        from_db = EquipamentoAmbiente.objects.get(
            equipamento=self.ID_EQUIPMENT_VALID, ambiente=self.ID_ENVIRONMENT_VALID)
        assert str(from_db.id) == str(equipment_type['id'])

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentEnvironmentUpdateTest(EquipmentEnvironmentConfigTest, AttrTest):

    def test_update_valid(self):
        mock = self.mock_update()
        self.client_autenticado().putXML(self.URL_UPDATE, {self.XML_KEY: mock})

        from_db = EquipamentoAmbiente.objects.get(
            equipamento=mock['id_equipamento'], ambiente=mock['id_ambiente'])
        is_router = 1 if from_db.is_router else 0

        assert is_router == mock['is_router']

    def test_update_nonexisten(self):
        mock = self.mock_nonexistent()
        response = self.client_autenticado().putXML(
            self.URL_UPDATE, {self.XML_KEY: mock})
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_update_no_permission(self):
        mock = self.mock_update()
        response = self.client_no_permission().putXML(
            self.URL_UPDATE, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_update_no_write_permission(self):
        mock = self.mock_update()
        response = self.client_no_write_permission().putXML(
            self.URL_UPDATE, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentEnvironmentAttrEquipamentTest(EquipmentEnvironmentConfigTest, AttrTest):
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


class EquipmentEnvironmentAttrEnvironmentTest(EquipmentEnvironmentConfigTest, AttrTest):
    KEY_ATTR = "id_ambiente"
    CODE_ERROR_NOT_FOUND = CodeError.ENVIRONMENT_NOT_FOUND

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


class EquipmentEnvironmentRemoveTest(EquipmentEnvironmentConfigTest, RemoveTest):

    def test_remove_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_ENVIRONMENT))
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_ENVIRONMENT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_ENVIRONMENT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_equipment_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_NONEXISTENT, self.ID_ENVIRONMENT))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_equipment_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.NEGATIVE_ATTR, self.ID_ENVIRONMENT))
        self._attr_invalid(response)

    def test_remove_equipment_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.LETTER_ATTR, self.ID_ENVIRONMENT))
        self._attr_invalid(response)

    def test_remove_equipment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ZERO_ATTR, self.ID_ENVIRONMENT))
        self._attr_invalid(response)

    def test_remove_equipment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.EMPTY_ATTR, self.ID_ENVIRONMENT))
        self._attr_invalid(response)

    def test_remove_equipment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.NONE_ATTR, self.ID_ENVIRONMENT))
        self._attr_invalid(response)

    def test_remove_environment_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_remove_environment_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_remove_environment_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_remove_environment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_remove_environment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_remove_environment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.NONE_ATTR))
        self._attr_invalid(response)
